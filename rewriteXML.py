#!/usr/bin/python

import argparse
import xml.etree
import xml.etree.ElementTree as ET

import sys
import os
import exceptions
import re
import pprint


#
# possibly the best and most obvious example for a build-need:
#
##   example0:       $      python2.7 rew*.py  -t overwrite  -C  hadoop-project \
##   example0:                    --find pom.xml   \
##   example0:                    --key+val jline.version=1.1.1.1.1 \
##   example0:                              hadoop.version=1.2.3.2.2.2.0
#

#
##   example1: rewriteXML   --find pom.xml   -t  overwrite  \
##                          --key+val jline.version=1.1.1.1.1   hadoop.version=1.2.3.2.2.2.0
#

#
##   example2: python2.7   rewriteXML.py       -f settings.xml   -t overwrite \
##                          -k    passphrase    -v    "Oh-you-kidding-me"
#

#
##   example3:        $   grep -i  pushOnSu UT-tez-dal.xml
##   example3:              <pushOnSuccess>false</pushOnSuccess>
##   example3:        $  rewriteXML -f UT-tez-dal.xml -t overwrite --key+val pushOnSuccess=true
##   example3:        > UT-tez-dal.xml
##   example3:        None
##   example3:        Processing pushOnSuccess=true
##   example3:        xpathRE = .//pushOnSuccess/..
##   example3:        propertyToReplace = pushOnSuccess
##   example3:        newContentToReplace = true
##   example3:        $   grep -i pushOnSu UT-tez-dal.xml
##   example3:              <pushOnSuccess>true</pushOnSuccess>e
#

#
##   example4:        $   fgrep -i  3.4.5  UT-tez-dal.xml
##   example4:              <version>3.4.5</version>
##   example4:        $  rewriteXML -f UT-tez-dal.xml -t overwrite -k version -v $zookeeper_jar_version --oldContents  3.4.5
##   example4:        > UT-tez-dal.xml
##   example4:        None
##   example4:        Processing version=3.4.5
##   example4:        xpathRE = .[version='3.4.5']
##   example4:        propertyToReplace = version
##   example4:        newContentToReplace = 1.2.3.2.3.0.0-235
##   example4:        $   grep -i version UT-tez-dal.xml
##   example4:              <version>1.2.3.2.3.0.0-235</version>
#
#
##   example5:        $   sed -n 5,15p < settings.xml
##   example5:        <servers>
##   example5:          <server>
##   example5:            <id>public</id>
##   example5:            <username>jenkins</username>
##   example5:            <password>Redacted</password>
##   example5:          </server>  
##   example5:          <server>
##   example5:            <id>LW-IN-QA</id>
##   example5:            <username>jenkins</username>
##   example5:            <password>Redacted</password>
##   example5:          </server> 
##   example5:        $   python2.7 rew*.py -t overwrite -k password -v NoWayINQA -f settings.xml --xpath ".//password/..[id='public']"
##   example5:        $   sed -n 4,15p < settings.xml
##   example5:          <id>public</id>
##   example5:          <username>jenkins</username>
##   example5:          <password>NoWayINQA</password>
##   example5:        </server>  
##   example5:        <server>
##   example5:          <id>LW-IN-QA</id>
##   example5:          <username>jenkins</username>
##   example5:          <password>Redacted</password>
##   example5:        </server>  
#


class PCParser(ET.XMLTreeBuilder):

    def __init__(self):
        """The comment-handler code is stolen from
        http://stackoverflow.com/questions/4474754/how-to-keep-comments-while-parsing-xml-using-python-elementtree
        """
        ET.XMLTreeBuilder.__init__(self)

       # assumes ElementTree 1.2.X

        self._parser.CommentHandler = self.handle_comment

    def handle_comment(self, data):
        self._target.start(ET.Comment, {})
        self._target.data(data)
        self._target.end(ET.Comment)



class plumbing:

    inputFile = None
    treeContents = None
    ns = None
    xmlLine = None

    def __init__(self, inFile=None, delimiter=":", force=False):
        """
        Read in an XML file:
        -  ignoring leading/trailing white space.
        -  grabbing the namespace-field (see the re.compile,
           a half-dozen lines below) for use in queries.
        The parsed elementree object is at self.root (and self.tree).
        """
               
        self.delimiter = delimiter
        self.force = force
        contents = None
        savedFirstLine = None
        firstlineRE = re.compile('(<.xml[^>]+>\s+)(.*)', flags=re.DOTALL)
        with open(inFile) as fd:
            contents = fd.read().strip()
            m = firstlineRE.match(contents)
            if m:
               (savedFirstLine,rest) = m.groups()
               self.xmlLine = savedFirstLine
               # print("savedFirstLine=" + savedFirstLine)
               contents = savedFirstLine+ "<container>" + rest + "</container>"
            else:
               contents = "<container>" + contents + "</container>"
        exprRE = re.compile('xmlns="(\S+)"')
        m = exprRE.search(contents)

        if m:
            self.ns = m.group(1)

        try:
            # this string-file operation is to be able
            # to pass a file-descriptor to the parse method().
	    # that is what populates self.tree.
            # (self.parsestring returns a different type.)

            import StringIO
            fstring = StringIO.StringIO(contents)
            parser = PCParser()
            self.tree = ET.parse(fstring, parser=parser)
        except ET.ParseError, e:
            print(contents)
            raise RuntimeError(inFile + ':' + str(e))

        self.root = self.tree.getroot()
        try:
            for el in self.root.iter():
                try:	# comments will hit a 'TypeError'.
                    if '}' in el.tag:
                        el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
                except TypeError: pass
        except AttributeError:
            for el in self.root.getiterator():
                try:	# comments will hit a 'TypeError'.
                    if '}' in el.tag:
                        el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
                except TypeError: pass
        self.choices = {}
        self.choices['overwrite'] = self.overwriteValue
        self.choices['appendlist'] = self.appendValueToList
        self.choices['deletelist'] = self.deleteValueFromList
        self.choices['deleteProperty'] = self.deleteProperty
        self.choices['addProperty'] = self.addProperty

    def getxmlLine(self):
        if self.xmlLine is None:
             return ""
        return self.xmlLine

    def isGoodChoice(self, choice=None):
        return(choice in self.choices)

    def getroot(self):
        return self.root

    def getNS(self):
        return self.ns

    def write(self, fd=None):
        if fd:
            self.tree.write(fd)

    def __str__(self):
	"""return a ascii representation of the object.  Since there
	is already a formatted verion, we use the existing code and
	fake a string-file to retrieve it.  """

        import StringIO
        fd = StringIO.StringIO()
        if self.tree:
            self.tree.write(fd)
            s = fd.getvalue()
            fd.close()
            return s

    def list(self):
        return str(self)

    def appendValueToList(self, item=None, propertyToReplace=None, newValue=None, oldContents=None):
        """for the element, <xxx>x,y,z</xxx> , append to the comma-separated list.
           (appending an already-existing list member is a no-op.)
        """
        oldValue = item.text
        if oldValue:
           l = oldValue.split(self.delimiter)
           if not (newValue in l):
               l.append(newValue)
               item.text = self.delimiter.join(l)
 

    def deleteValueFromList(self, item=None, propertyToReplace=None, newValue=None, oldContents=None):
        """for the element, <xxx>x,y,z</xxx> , delete from the comma-separated list.
           (appending an already-existing list member is a no-op.)
        """
        oldValue = item.text
        if oldValue:
           l = oldValue.split(self.delimiter)
           if newValue in l:
                l.remove(newValue)
                item.text = self.delimiter.join(l)
    
    def overwriteValue(self, item=None, propertyToReplace=None, newValue=None, oldContents=None):
        # print("OverwriteValue(%s)" % propertyToReplace)
        
        if item is None:	# TODO: replace this code.
            if not self.force:
                raise RuntimeError, "Cannot create new element without permission to do so."
            ET.SubElement(item, tag=propertyToReplace, text=newValue)
        else:
            # pprint.pprint(item)
            if oldContents and item.text != oldContents:
                return
            item.text = newValue

    def addProperty(self, item=None, propertyToReplace=None, newValue=None, oldContents=None):
        x = item.find(propertyToReplace)
        if x is None:
            ET.SubElement(item, tag=propertyToReplace, text=newValue)
        else:
            raise RuntimeError, "Trying to add an element that is already there."

    def deleteProperty(self, item=None, propertyToReplace=None, newValue=None, oldContents=None):
        x = item.find(propertyToReplace)
        if x is None:
            raise RuntimeError, "Cannot delete element  - it is not found!"
        item.remove(x)
        
    def substitute(
        self,
        property,
        newValue,
        xpathRE=None,
        choice="overwrite",
        oldContents=None
        ):
        """ The substitution itself - set value PROPERTY to the value given, whereever it appears.
          (Works as of Feb 11.)"""

        if xpathRE is None:
            from string import Template
            xpathRE = '*//%s' % property
        print("( xpath being used is: %s )" % xpathRE)
        fcnToCall = None
        
        if self.isGoodChoice(choice):
            fcnToCall = self.choices[choice]
        else:
            raise Exception("choice (overwrite/appendlist/delete/etc not passed to 'substitute'")
            
        return self.updateProperty(xpathRE=xpathRE,
                                    propertyToReplace=property,
                                    newContentToReplace=newValue,
                                    fcn=fcnToCall, oldContents=oldContents)
    def updateProperty(
        self,
        xpathRE=None,
        propertyToReplace=None,
        newContentToReplace=None,
        fcn=overwriteValue,
        oldContents=None
        ):
        """Make a new property based on the xpath: if exists, update value; if not, flag error.
      example xpathRE:    ".//hadoop.version/.."   (read: all nodes that have a hadoop.version property.)
      (Works as of Feb 11.)"""

        if not (xpathRE and propertyToReplace and newContentToReplace is not None):
            raise RuntimeError, \
                'Did not pass xpath/name/val to updateProperty'

        print("print xpath=" + xpathRE)
        items = xmlObject.getroot().findall(xpathRE)
        # pprint.pprint(items)
        if items is None:
            raise RuntimeError, \
                'Trying to update property %s but could not locate it using xpath="%s"' \
                % (propertyToReplace, xpathRE)
        for item in items:
            try: 
                fcn(item, propertyToReplace, newContentToReplace, oldContents)

            except Exception as e:
                print(str(e))
                pprint.pprint(e)
                raise
        return str(self)

    def debug(self, msg=None):
        if msg:
            print self.inFile + ': ' + str(msg)
        print self.list()


## whatToReplace = ".//year/..[@%s='%s']" % (attributeToReplace, oldContentToReplace)
##
## for country in root.findall(whatToReplace):
##       country.set(attributeToReplace, newContentToReplace)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Edit XML file')
    parser.add_argument(
        '--command',
        '--task',
        '-t',
        dest='task',
        choices=['overwrite', 'appendlist', 'deletelist', 'list', 'addProperty',  'deleteProperty' ], default='list',
        )
    parser.add_argument(
        '--sep',
        '--separator',
        '--delimiter',
        '-d',
        dest='delimiter',
        default=","
        )
    parser.add_argument(
        '--force',
        '-F',
        dest='force',
        action='store_true', default=False)
    parser.add_argument(
        '-C',
        '--chdir',
        dest='chdir',
        default=None
        )
    parser.add_argument(
        '--dryrun',
        '--dry-run',
        '-n',
        dest='dryrun',
        type=bool,
        default=False,
        )
    parser.add_argument(
        '--oldContents',
        dest='oldContents',
        type=str,
        default=None,
        )
    parser.add_argument(
        '--xpath',
        '--expr',
        '-e',
        dest='xpathExpression',
        type=str,
        required=False,
        default=None,
        )
    parser.add_argument('--new-key', '-k', dest='key', type=str)
    parser.add_argument('--new-val', '--new-value', '-v', dest='val',
                        type=str, default=None)
    parser.add_argument('--key+val', dest='keyANDvalue', nargs='+',
                        type=str, default=None)
    parser.add_argument(
        '--file',
        '-f',
        dest='inFile',
        action='append',
        type=str,
        required=False,
        )
    parser.add_argument('--find', dest='recursiveFilename',
                        required=False, default=None)

    args = parser.parse_args()

    if args.chdir:
        try:
             os.chdir(args.chdir)
        except OSError as e:
             print(str(e))
             print("pwd=" + os.getcwd())
             dirs=os.listdir(os.getcwd)
             for d in dirs:  print(">" + d)
             raise
    filesToProcess = []
    if args.recursiveFilename:
        filesToProcess = [os.path.join(dp, f) for (dp, dn,
                          filenames) in os.walk('.') for f in filenames
                          if f == args.recursiveFilename]
        print 'Will look at files: '
    if args.inFile:
        for f in args.inFile:
            filesToProcess.append(f)
    for r in filesToProcess:
        print '> ' + r

    if len(filesToProcess) == 0:
        raise RuntimeError("You didn't give me files to process via --file or --find!")
    equalsRE = re.compile("^([^=]*)=(.*)")
    for inFile in filesToProcess:
        xmlObject = plumbing(inFile=inFile, delimiter=args.delimiter, force=args.force)
        if args.task == 'list':
            print xmlObject.list()
        if xmlObject.isGoodChoice(args.task):
            if args.keyANDvalue:
                for arg in args.keyANDvalue:
                    # print 'Processing ' + arg
                    m = equalsRE.match(arg)
                    (k, v) = m.groups()
                    xmlObject.substitute(property=k, newValue=v, choice=args.task, oldContents=args.oldContents, xpathRE=args.xpathExpression)
            elif args.key and args.val is not None:
                xmlObject.substitute(property=args.key,
                        newValue=args.val, choice=args.task, oldContents=args.oldContents, xpathRE=args.xpathExpression)
            else:
                raise RuntimeError, \
                    'No -k/-v given for %s and no --key+val x=1 y=2 ... given.' \
                    % args.task

        if args.dryrun:
            print 'Not overwriting files.'
            print 'file %s ------\n' % inFile + xmlObject.list()
        else:
            with open(inFile, 'w') as fd:
                fd.write(xmlObject.getxmlLine())
                spares = []
                for d in xmlObject.getroot().getchildren():
                   if True:
                   # try:
                      if d.tag is ET.Comment:
                          fd.write("<!--" + d.text + "-->" + "\n")
                      else:
                          spares.append(d)
                   # except AttributeError: pass
                spare = spares.pop()
                # # TODO: verify that len(spares) == 1
                # # TODO: move any attributes FROM root to the new root.
                for (a,v) in xmlObject.getroot().items():
                   spare.set(a,v)
                ns = xmlObject.getNS()
                if ns:
                    spare.set("xmlns",ns)
                xmlObject.tree._setroot(spare)
                xmlObject.tree.write(fd)
