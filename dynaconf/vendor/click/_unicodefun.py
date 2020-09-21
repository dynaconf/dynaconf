import codecs,os
def _verify_python_env():
	M='.utf8';L='.utf-8';J=None;I='ascii'
	try:import locale as A;G=codecs.lookup(A.getpreferredencoding()).name
	except Exception:G=I
	if G!=I:return
	B=''
	if os.name=='posix':
		import subprocess as D
		try:C=D.Popen(['locale','-a'],stdout=D.PIPE,stderr=D.PIPE).communicate()[0]
		except OSError:C=b''
		E=set();H=False
		if isinstance(C,bytes):C=C.decode(I,'replace')
		for K in C.splitlines():
			A=K.strip()
			if A.lower().endswith((L,M)):
				E.add(A)
				if A.lower()in('c.utf8','c.utf-8'):H=True
		B+='\n\n'
		if not E:B+='Additional information: on this system no suitable UTF-8 locales were discovered. This most likely requires resolving by reconfiguring the locale system.'
		elif H:B+='This system supports the C.UTF-8 locale which is recommended. You might be able to resolve your issue by exporting the following environment variables:\n\n    export LC_ALL=C.UTF-8\n    export LANG=C.UTF-8'
		else:B+=f"This system lists some UTF-8 supporting locales that you can pick from. The following suitable locales were discovered: {', '.join(sorted(E))}"
		F=J
		for A in (os.environ.get('LC_ALL'),os.environ.get('LANG')):
			if A and A.lower().endswith((L,M)):F=A
			if A is not J:break
		if F is not J:B+=f"\n\nClick discovered that you exported a UTF-8 locale but the locale system could not pick up from it because it does not exist. The exported locale is {F!r} but it is not supported"
	raise RuntimeError(f"Click will abort further execution because Python was configured to use ASCII as encoding for the environment. Consult https://click.palletsprojects.com/unicode-support/ for mitigation steps.{B}")