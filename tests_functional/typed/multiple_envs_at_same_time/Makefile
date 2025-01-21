.PHONY: test

test:
	python app.py
	
	python app.py | grep "HOST='default.com'"
	python app.py | grep "DEBUG=False"

	BLARG_MODE=production python app.py | grep "HOST='production.com'"
	
	BLARG_MODE=extra python app.py | grep "HOST='default.com'"
	BLARG_MODE=extra python app.py | grep "DEBUG=True"
	BLARG_MODE=extra python app.py | grep "PORT=1234"

	BLARG_MODE=production,extra python app.py | grep "HOST='production.com'"
	BLARG_MODE=production,extra python app.py | grep "PORT=1234"
	BLARG_MODE=production,extra python app.py | grep "DEBUG=True"
	
	BLARG_MODE=production,extra dynaconf -i app.settings inspect -k COUNTER
	BLARG_MODE=production,extra dynaconf -i app.settings inspect -k COLORS
	BLARG_MODE=production,extra dynaconf -i app.settings inspect -k PERSON
	BLARG_MODE=production,extra dynaconf -i app.settings inspect -k INITIAL
	BLARG_MODE=production,extra dynaconf -i app.settings inspect -k CALCULATED
	BLARG_MODE=production,extra dynaconf -i app.settings inspect -k XCALCULATED

