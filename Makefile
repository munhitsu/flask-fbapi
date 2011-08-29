.DEFAULT_GOAL = development
.PHONY = development clean
ARCHFLAGS = "-arch i386 -arch x86_64"


bootstrap.py :
	wget http://svn.zope.org/*checkout*/zc.buildout/trunk/bootstrap/bootstrap.py

bin/buildout : bootstrap.py
	python bootstrap.py -d

development : bin/buildout
	env ARCHFLAGS=${ARCHFLAGS} bin/buildout

clean :
	rm -rf bin develop-eggs eggs parts .installed.cfg downloads bootstrap.py
	find . -name "*~" -exec rm {} \;
	find . -name "DEADJOE" -exec rm {} \;
	find . -name "*.pyc" -exec rm {} \;
