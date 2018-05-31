
import plex


#!/usr/bin/env python3
# -*- coding: utf_8 -*-

"""
Example of recursive descent parser written by hand using plex module as scanner
NOTE: This progam is a language recognizer only.
Grammar :


<Program>             ->      Stmt_list #           (Ξ²ΞΏΞ·ΞΈΞ·Ο„ΞΉΞΊΟΟ‚ ΞΊΞ±Ξ½ΟΞ½Ξ±Ο‚!)
Stmt_list             ->      Stmt Stmt_list | Ξµ
Stmt                  ->      id = Expr | print Expr
Expr                  ->      OrExpresion OrExpresion_tail
OrExpresion_tail      ->      or OrExpresion OrExpresion_tail | Ξµ
OrExpresion           ->      AndExpresion AndExpresion_tail
AndExpresion_tail     ->      and AndExpresion AndExpresion_tail | Ξµ
AndExpresion          ->      NotExpresion NotExpresion_tail
NotExpresion          ->      not | Ξµ
NotExpresion_tail     ->      (Expr) | var | true | 1 | 0 | false | t | f



print: Ο„ΞΏ keyword 'print'
id,var: ΟΞ½ΞΏΞΌΞ± ΞΌΞµΟ„Ξ±Ξ²Ξ»Ξ·Ο„Ξ®Ο‚


B)                
                        FirstSETs                                 FollowSETs
Stmt_list       	id, print, Ξµ	                               #
Stmt            	id, print	                               id, print, #
Expr            	not, (, var, true, 1, 0, false, t, f	       ), id, print, #
OrExpresion_tail	or, Ξµ	                                       ), id, print, #
OrExpresion       	not, (, var, true, 1, 0, false, t, f	       or,) ,id , print, #
AndExpresion_tail	and, Ξµ	                                       or,) ,id , print, #
AndExpresion      	not, (, var, true, 1, 0, false, t, f	       and, or,) ,id , print, #
NotExpresion      	not, Ξµ	                                       (, var, true, 1, 0, false, t, f
NotExpresion_tail	(, var, true, 1, 0, false, t, f	               and, or,) ,id , print, #



  
"""


import plex
from plex import *



class ParseError(Exception):
        """ A user defined exception class, to describe parse errors. """
        pass



class MyParser:
        """ A class encapsulating all parsing functionality
        for a particular grammar. """
        
        def create_scanner(self,fp):
                """ Creates a plex scanner for a particular grammar 
                to operate on file object fp. """

                # define some pattern constructs
                letter = plex.Range("AZaz")
                digit = plex.Range("09")

                id = plex.Rep1(letter | digit)
                var = plex.Rep1(letter | digit)
                operator = plex.Any("!?()=#")             
                space = plex.Any(" \t\n")

                # the scanner lexicon - constructor argument is a list of (pattern,action ) tuples
                lexicon = plex.Lexicon([
                        (operator,plex.TEXT),
                        (space,plex.IGNORE),
                        (Str("id"),plex.TEXT),
                        (Str("print"),plex.TEXT),
                        (Str("or"),plex.TEXT),
                        (Str("and"),plex.TEXT),
                        (Str("not"),plex.TEXT),
                        (var,'var')
                ])
                
                # create and store the scanner object
                self.scanner = plex.Scanner(lexicon,fp)
                
                # get initial lookahead
                self.la,self.val = self.next_token()


        def next_token(self):
                """ Returns tuple (next_token,matched-text). """
                
                return self.scanner.read()              

        
        def position(self):
                """ Utility function that returns position in text in case of errors.
                Here it simply returns the scanner position. """
                
                return self.scanner.position()
        

        def match(self,token):
                """ Consumes (matches with current lookahead) an expected token.
                Raises ParseError if anything else is found. Acquires new lookahead. """ 
                
                if self.la==token:
                        self.la,self.val = self.next_token()
                else:
                        raise ParseError("found {} instead of {}".format(self.la,token))
        
        
        def parse(self,fp):
                """ Creates scanner for input file object fp and calls the parse logic code. """
                
                # create the plex scanner for fp
                self.create_scanner(fp)
                
                # call parsing logic
                self.Stmt_list()
        
                        
        def Stmt_list(self):
                """ Stmt_list  -> Stmt Stmt_list | Ξµ"""
                if self.la=='id' or self.la=='print':
                        self.Stmt()
                elif self.la=='#':       # from FOLLOW set!
                        return  
                else:
                        raise ParseError("In rule Stmt_list: id, print or # expected read:",self.la )
                                
        
        def Stmt(self):
                """ Stmt  -> id = Expr | print Expr """
                if self.la=='id':
                        self.match('id')
                        self.match('=')
                        self.Expr()
                elif self.la=='print':
                        self.match('print')
                        self.Expr()
                else:
                        raise ParseError("In rule Stmt: id or print expected")
        
        
        def Expr(self):
                """ Expr ->  OrExpresion OrExpresion_tail """
                if self.la=='not' or self.la=='(' or self.la=='var' or self.la=='true' or self.la=='false' or self.la=='t' or self.la=='f' or self.la=='0' or self.la=='1':
                        self.OrExpresion()
                        self.OrExpresion_tail()
                else:
                        raise ParseError("In rule Expr: not, (, var, true, 1, 0, false, t, or f  is expected !!", self.la)
                                

        def OrExpresion_tail(self):
                """ OrExpresion_tail  -> or OrExpresion OrExpresion_tail | Ξµ """
                if self.la=='or':
                        self.match('or')
                        self.OrExpresion()
                        self.OrExpresion_tail()
                elif self.la==')' or self.la=='var' or self.la==' print' or self.la=='#':    # from FOLLOW set!
                        return  
                else:
                        raise ParseError("In rule OrExpresion_tail: or, ), var, print, # is expected")

        def OrExpresion(self):
                """ OrExpresion  -> AndExpresion AndExpresion_tail """
                
                if self.la=='not' or self.la=='(' or self.la=='var' or self.la=='true' or self.la=='false' or self.la=='t' or self.la=='f' or self.la=='0' or self.la=='1':
                        self.AndExpresion()
                        self.AndExpresion_tail()
                else:
                        raise ParseError("In rule OrExpresion: not, (, var, true, 1, 0, false, t, or f is expected")

        def AndExpresion_tail(self):
                """ AndExpresion_tail  -> and AndExpresion AndExpresion_tail |Ξµ """
                if self.la=='and':
                        self.match('and')
                        self.AndExpresion()
                        self.AndExpresion_tail()
                elif self.la=='or' or self.la==')' or self.la=='var' or self.la=='print' or self.la=='#' :
                        return
                else:
                        raise ParseError("In rule AndExpresion_tail: and, or, ), var, print or # is expected")

        def AndExpresion(self):
                """ AndExpresion  -> NotExpresion NotExpresion_tail """
                if self.la=='not' or self.la=='(' or self.la=='var' or self.la=='true' or self.la=='false' or self.la=='t' or self.la=='f' or self.la=='0' or self.la=='1':
                        self.NotExpresion()
                        self.NotExpresion_tail()
                else:
                        raise ParseError("In rule AndExpresion: not, (, var, true, 1, 0, false, t, or f is expected")

        def NotExpresion(self):
                """ NotExpresion  ->  not |Ξµ """
                if self.la=='not':
                        self.match('not')
                elif self.la=='(' or self.la=='var' or self.la=='true' or self.la=='false' or self.la=='t' or self.la=='f' or self.la=='0' or self.la=='1' : # from FOLLOW set!
                        return
                else:
                        raise ParseError("In rule NotExpresion: not, (, var, true, 1, 0, false, t, or f is expected")

        def NotExpresion_tail(self):
                """ NotExpresion_tail  -> (Expr) | var | true, 1, 0, false, t, f """
                if self.la=='(':
                        self.match('(')
                        self.Expr()
                        self.match(')')
                elif self.la=='var' :
                        self.match('var')
                elif self.la=='true' :
                        self.match('true')
                elif self.la=='false' :
                        self.match('false')
                elif self.la=='t' :
                        self.match('t')
                elif self.la=='f' :
                        self.match('f')
                elif self.la=='0' :
                        self.match('0')
                elif self.la=='1' :
                        self.match('1')
                else:
                        raise ParseError("In rule NotExpresion_tail: (Expr), id,  true, 1, 0, false, t, or f is expected")


						
						

                        
# the main part of prog

# create the parser object
parser = MyParser()

# open file for parsing
with open("input_boolean.txt","r") as fp:

        # parse file
        try:
                parser.parse(fp)
        except plex.errors.PlexError:
                _,lineno,charno = parser.position()     
                print("Scanner Error: at line {} char {}".format(lineno,charno+1))
        except ParseError as perr:
                _,lineno,charno = parser.position()     
                print("Parser Error: {} at line {} char {}".format(perr,lineno,charno+1))
