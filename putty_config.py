#!python

from winreg import OpenKey, QueryInfoKey, EnumKey, EnumValue, QueryValueEx, \
	SetValueEx, HKEY_CURRENT_USER,KEY_ALL_ACCESS,KEY_READ
from optparse import OptionParser, OptionGroup
import fnmatch
import sys

def registry_subkeys(key) :
	ret = list()
	subkeys, subvals, mtime = QueryInfoKey(key)
	for i in range(subkeys) :
		name = EnumKey(key,i)
		ret.append(name)
	return ret

def registry_values(key) :
	ret = dict()
	subkeys, subvals, mtime = QueryInfoKey(key)
	for i in range(subvals) :
		name,data,type = EnumValue(key,i)
		ret[name]=data
	return ret

class PuttyConfig :
	def __init__(self,parent = None) :
		if parent :
			self.r_putty = parent
		else :
			self.r_putty = OpenKey(HKEY_CURRENT_USER,
				r'Software\SimonTatham\PuTTY',0,KEY_READ)

	def sessions(self) :
		sess = OpenKey(self.r_putty,'Sessions',0,KEY_READ)
		return registry_subkeys(sess)

	def get_config(self,name) :
		sess = OpenKey(self.r_putty,r'Sessions\%s'%(name),
			0,KEY_READ)
		return registry_values(sess)

	def set_config_value(self,sess_name,par_name,par_value) :
		sess = OpenKey(self.r_putty,r'Sessions\%s'%(sess_name),
			0,KEY_ALL_ACCESS)
		try :
			rv_val, rv_type = QueryValueEx(sess,par_name)
#			print 'Value: %s, %s, %s, python type %s'%(
#				par_value,rv_val,rv_type,type(rv_val))
			# try to encode the given value as the returned
			# python type
			new_val = type(rv_val)(par_value)
			SetValueEx(sess,par_name,0,rv_type,new_val)
		except WindowsError as e :
			if e.winerror == 2 :
				return False # Key not found.
			print('Windows Error: ',e)
			return False
		return True

if __name__ == '__main__' :
	parser = OptionParser(usage='%prog [options] [Session]')
	pgrp = OptionGroup(parser,'Commands')
	pgrp.add_option('-l','--list',action='store_true',
		dest='list',default=False,help='List sessions.')
	pgrp.add_option('-g','--get',action='store',type='string',
		dest='get',default=False,help='Get parameter NAME',
		metavar='NAME');
	pgrp.add_option('-s','--set',action='store',type='string',
		dest='set',default=False,help='Set parameter NAME to VALUE',
		metavar='NAME=VALUE');
	pgrp.add_option('-d','--dump',action='store_true',
		dest='dump',default=False,help='Dump session.',
		metavar='SESSION')
	pgrp.add_option('-m','--match',action='store',type='string',
		dest='match',default=None,help='Match (glob) session when dumping.',
		metavar='PATTERN')
	parser.add_option_group(pgrp)

	opts,args = parser.parse_args()
	PC = PuttyConfig()

	# get all sessions, apply (optinal) filter.
	sessions = PC.sessions()
	if len(args) >= 1 :
		filtsess = [s for s in sessions if fnmatch.fnmatch(s,args[0])]
		print('%d session(s) in total, %d match filter \"%s\".'%(
			len(sessions),len(filtsess),args[0]))
		sessions = filtsess
	else :
		print('%d session(s) in total.'%(len(sessions)))

	if opts.list :
		for s in sessions :
			print('\t%s'%(s))
		sys.exit(0)

	if opts.dump :
		if len(sessions) != 1 :
			print('You have to specify one session! (list them using -l)')
			sys.exit(1)
		print('Parameter Name       Parameter Value')
		print('--------------------:----------------------------------------')
		cfg = PC.get_config(sessions[0])
		for pn,pv in cfg.items() :
			if opts.match and not fnmatch.fnmatch(pn,opts.match) :
				continue
			print('%-20s %s'%(pn,pv))
		sys.exit(0)


	if opts.get :
		print('')
		print('Session              Parameter %s'%(opts.get))
		print('--------------------:----------------------------------------')
		for s in sessions :
			cfg = PC.get_config(s)
			val = cfg.get(opts.get,'-')
			print('%-20s %s'%(s,val))
		sys.exit(0)

	if opts.set :
		name,val = opts.set.split('=',1)
		print('Updating parameter \'%s\' to value \'%s\'.'%(name,val))
		for s in sessions :
			res = PC.set_config_value(s,name,val)
			if res :
				print('\t%-20s: ok'%(s))
			else :
				print('\t%-20s: not updated'%(s))
		sys.exit(0)

	print('No command given. Maybe you should try --help?')
