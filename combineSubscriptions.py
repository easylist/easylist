#!/usr/bin/env python
# coding: utf-8

# The contents of this file are subject to the Mozilla Public License
# Version 1.1 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/

import sys, os, re, subprocess, urllib2, time, traceback, codecs, hashlib, base64
from getopt import getopt, GetoptError

acceptedExtensions = {
  '.txt': True,
}
ignore = {
  'Apache.txt': True,
  'CC-BY-SA.txt': True,
  'GPL.txt': True,
  'MPL.txt': True,
}
verbatim = {
  'COPYING': True,
}

def combineSubscriptions(sourceDir, targetDir, timeout=30):
  global acceptedExtensions, ignore, verbatim

  if not os.path.exists(targetDir):
    os.makedirs(targetDir, 0755)

  known = {}
  for file in os.listdir(sourceDir):
    if file in ignore or file[0] == '.' or not os.path.isfile(os.path.join(sourceDir, file)):
      continue
    if file in verbatim:
      processVerbatimFile(sourceDir, targetDir, file)
    elif not os.path.splitext(file)[1] in acceptedExtensions:
      continue
    else:
      try:
        processSubscriptionFile(sourceDir, targetDir, file, timeout)
      except:
        print >>sys.stderr, 'Error processing subscription file "%s"' % file
        traceback.print_exc()
        print >>sys.stderr
      known[os.path.splitext(file)[0] + '.tpl'] = True
      known[os.path.splitext(file)[0] + '.tpl.gz'] = True
    known[file] = True
    known[file + '.gz'] = True

  for file in os.listdir(targetDir):
    if file[0] == '.':
      continue
    if not file in known:
      os.remove(os.path.join(targetDir, file))

def conditionalWrite(filePath, data):
  changed = True
  if os.path.exists(filePath):
    handle = codecs.open(filePath, 'rb', encoding='utf-8')
    oldData = handle.read()
    handle.close()

    checksumRegExp = re.compile(r'^.*!\s*checksum[\s\-:]+([\w\+\/=]+).*\n', re.M | re.I)
    oldData = re.sub(checksumRegExp, '', oldData)
    oldData = re.sub(r'\s*\d+ \w+ \d+ \d+:\d+ UTC', '', oldData)
    newData = re.sub(checksumRegExp, '', data)
    newData = re.sub(r'\s*\d+ \w+ \d+ \d+:\d+ UTC', '', newData)
    if oldData == newData:
      changed = False
  if changed:
    handle = codecs.open(filePath, 'wb', encoding='utf-8')
    handle.write(data)
    handle.close()
    try:
      subprocess.Popen(['7za', 'a', '-tgzip', '-mx=9', '-bd', '-mpass=15', filePath + '.gz', filePath], stdout=subprocess.PIPE).communicate()
    except:
      print >>sys.stderr, 'Failed to compress file %s. Please ensure that p7zip is installed on the system.' % filePath

def processVerbatimFile(sourceDir, targetDir, file):
  handle = codecs.open(os.path.join(sourceDir, file), 'rb', encoding='utf-8')
  conditionalWrite(os.path.join(targetDir, file), handle.read())
  handle.close()

def processSubscriptionFile(sourceDir, targetDir, file, timeout):
  filePath = os.path.join(sourceDir, file)
  handle = codecs.open(filePath, 'rb', encoding='utf-8')
  lines = map(lambda l: re.sub(r'[\r\n]', '', l), handle.readlines())
  handle.close()

  header = ''
  if len(lines) > 0:
    header = lines[0]
    del lines[0]
  if not re.search(r'\[Adblock(?:\s*Plus\s*([\d\.]+)?)?\]', header, re.I):
    raise Exception('This is not a valid Adblock Plus subscription file.')

  lines = resolveIncludes(filePath, lines, timeout)
  lines = filter(lambda l: l != '' and not re.search(r'!\s*checksum[\s\-:]+([\w\+\/=]+)', l, re.I), lines)

  writeTPL(os.path.join(targetDir, os.path.splitext(file)[0] + '.tpl'), lines)

  checksum = hashlib.md5()
  checksum.update((header + '\n' + '\n'.join(lines) + '\n').encode('utf-8'))
  lines.insert(0, '! Checksum: %s' % re.sub(r'=', '', base64.b64encode(checksum.digest())))
  lines.insert(0, header)
  conditionalWrite(os.path.join(targetDir, file), '\n'.join(lines) + '\n')

def resolveIncludes(filePath, lines, timeout, level=0):
  if level > 5:
    raise Exception('There are too many nested includes, which is probably the result of a circular reference somewhere.')

  result = []
  for line in lines:
    match = re.search(r'^\s*%include\s+(.*)%\s*$', line)
    if match:
      file = match.group(1)
      newLines = None
      if re.match(r'^https?://', file):
        result.append('! *** Fetched from: %s ***' % file)

        request = urllib2.urlopen(file, None, timeout)
        charset = 'utf-8'
        contentType = request.headers.get('content-type', '')
        if contentType.find('charset=') >= 0:
          charset = contentType.split('charset=', 1)[1]
        newLines = unicode(request.read(), charset).split('\n')
        newLines = map(lambda l: re.sub(r'[\r\n]', '', l), newLines)
        newLines = filter(lambda l: not re.search(r'^\s*!.*?\bExpires\s*(?::|after)\s*(\d+)\s*(h)?', l, re.M | re.I), newLines)
      else:
        result.append('! *** %s ***' % file)

        parentDir = os.path.dirname(filePath)
        includePath = os.path.join(parentDir, file)
        relPath = os.path.relpath(includePath, parentDir)
        if len(relPath) == 0 or relPath[0] == '.':
          raise Exception('Invalid include "%s", needs to be an HTTP/HTTPS URL or a relative file path' % file)

        handle = codecs.open(includePath, 'rb', encoding='utf-8')
        newLines = map(lambda l: re.sub(r'[\r\n]', '', l), handle.readlines())
        newLines = resolveIncludes(includePath, newLines, timeout, level + 1)
        handle.close()

      if len(newLines) and re.search(r'\[Adblock(?:\s*Plus\s*([\d\.]+)?)?\]', newLines[0], re.I):
        del newLines[0]
      result.extend(newLines)
    else:
      if line.find('%timestamp%') >= 0:
        if level == 0:
          line = line.replace('%timestamp%', time.strftime('%d %b %Y %H:%M UTC', time.gmtime()))
        else:
          line = ''
      result.append(line)
  return result

def writeTPL(filePath, lines):
  result = []
  result.append('msFilterList')
  for line in lines:
    if re.search(r'^!', line):
      # This is a comment. Handle "Expires" comment in a special way, keep the rest.
      match = re.search(r'\bExpires\s*(?::|after)\s*(\d+)\s*(h)?', line, re.I)
      if match:
        interval = int(match.group(1))
        if match.group(2):
          interval = int(interval / 24)
        result.append(': Expires=%i' % interval)
      else:
        result.append(re.sub(r'!', '#', re.sub(r'--!$', '--#', line)))
    elif line.find('#') >= 0:
      # Element hiding rules are not supported in MSIE, drop them
      pass
    else:
      # We have a blocking or exception rule, try to convert it
      origLine = line

      isException = False
      if line[0:2] == '@@':
        isException = True
        line = line[2:]

      hasUnsupportedOptions = False
      requiresScript = False
      match = re.search(r'^(.*?)\$(.*)', line)
      if match:
        # This rule has options, check whether any of them are important
        line = match.group(1)
        options = match.group(2).replace('_', '-').lower().split(',')

        # A number of options are not supported in MSIE but can be safely ignored, remove them
        options = filter(lambda o: not o in ('', 'third-party', '~third-party', 'match-case', '~match-case', '~object-subrequest', '~donottrack'), options)

        # Also ignore domain negation of whitelists
        if isException:
          options = filter(lambda o: not o.startswith('domain=~'), options)

        if 'donottrack' in options:
          # Rules with donottrack option should always be removed
          hasUnsupportedOptions = True
        elif 'object-subrequest' in options and len(options) == 1:
          # The rule applies only to object subrequests, it is not supported in MSIE
          hasUnsupportedOptions = True
        elif 'script' in options and len(options) == 1:
          # The rule applies only to scripts, we can deal with that - somewhat
          requiresScript = True
        elif len(options) > 0:
          # The rule has further options that we don't support. For exception
          # rules we still ignore that if the rule isn't restricted to a single
          # domain, this should hopefully prevent some false positives.
          if isException:
            hasUnsupportedOptions = any([o.startswith('domain=') for o in options])
          else:
            hasUnsupportedOptions = True

      if hasUnsupportedOptions:
        result.append('# ' + origLine)
      else:
        line = line.replace('^', '/') # Assume that separator placeholders mean slashes

        # Try to extract domain info
        domain = None
        match = re.search(r'^(\|\||\|\w+://)([^*:/]+)(:\d+)?(/.*)', line)
        if match:
          domain = match.group(2)
          line = match.group(4)
        else:
          # No domain info, remove anchors at the rule start
          line = re.sub(r'^\|\|', 'http://', line)
          line = re.sub(r'^\|', '', line)
        # Remove anchors at the rule end
        line = re.sub(r'\|$', '', line)
        # Emulate $script by appending *.js to the rule
        if requiresScript:
          line += '*.js'
        if line.startswith('/*'):
          line = line[2:]
        if domain:
          line = '%sd %s %s' % ('+' if isException else '-', domain, line)
          line = re.sub(r'\s+/$', '', line)
          result.append(line)
        elif isException:
          # Exception rules without domains are unsupported
          result.append('# ' + origLine)
        else:
          result.append('- ' + line)
  conditionalWrite(filePath, '\n'.join(result) + '\n')

def usage():
  print '''Usage: %s [source_dir] [output_dir]

Options:
  -h          --help              Print this message and exit
  -t seconds  --timeout=seconds   Timeout when fetching remote subscriptions
''' % os.path.basename(sys.argv[0])

if __name__ == '__main__':
  try:
    opts, args = getopt(sys.argv[1:], 'ht:', ['help', 'timeout='])
  except GetoptError, e:
    print str(e)
    usage()
    sys.exit(2)

  sourceDir, targetDir =  '.', 'subscriptions'
  if len(args) >= 1:
    sourceDir = args[0]
  if len(args) >= 2:
    targetDir = args[1]

  timeout = 30
  for option, value in opts:
    if option in ('-h', '--help'):
      usage()
      sys.exit()
    elif option in ('-t', '--timeout'):
      timeout = int(value)

  if os.path.exists(os.path.join(sourceDir, '.hg')):
    # Our source is a Mercurial repository, try updating
    subprocess.Popen(['hg', '-R', sourceDir, 'pull', '--update']).communicate()

  combineSubscriptions(sourceDir, targetDir, timeout)
