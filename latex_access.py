'''This module provides translations of lines of LaTeX into either braille or spoken output.'''

import re
import types

# Regular expression to match LaTeX commands
latex_command=re.compile(r"\\(([a-zA-Z]+)|[,!;])")

class translator:
    '''Class from which all translators will inherit.'''
    def __init__(self):
        self.table={"\\mbox":self.text,"\\text":self.text,"\\textrm":self.text,"\\textit":self.text,"\\mathrm":self.text,"\\textbf":self.text,"\\displaystyle":self.displaystyle,"\\phantom":self.remove}
        
        self.remove_dollars=False
    def translate(self,input):        
        '''This translates the string in input using the translation table
        
        Returns string.'''

        output=""
        i=0
        while (i<len(input)):
            # Test if we have a LaTeX command
            if input[i] == "\\":
                match=latex_command.match(input[i:])
                if match:
                    curr=match.group()
                else:
                    curr="\\"
                    
            else:
                curr=input[i]
                
            if curr in self.table:
                i+=len(curr)
                if type(self.table[curr]) == types.StringType:
                    output += self.table[curr]

                elif type(self.table[curr]) == types.MethodType:
                    translation=self.table[curr](input,i)
                    output+=translation[0]
                    i=translation[1]
            

            else:
                output += curr
                i += len(curr)
        return output

    def text(self,input, start):
        '''Used to translate text, as in mbox and text

        returns touple.'''
        arg=get_arg(input,start)
        return (arg[0],arg[1])

    def displaystyle(self,input, start):
        '''Removes the displaystile command but translates its argument.

        Returns touple.'''
        arg=get_arg(input,start)
        return (self.translate(arg[0]),arg[1])
    
    def remove(self,input,start):
        '''Used to remove a command and its argument totally from the translation.
        Useful for phantom commands.  

        Returns touple.'''
        arg=get_arg(input,start)
        return("",arg[1])


    def general_command(self,input, start, delimitors):
        '''Used to process a command when the required translation is just the arguments joined by appropriate delimitors. 
        The 3rd argument is a list of such delimitors, the 1st element of which goes before the 1st argument of the command, etc.

        Returns usual touple.'''
        translation=delimitors[0]
        for delim  in delimitors[1:]:
            arg=get_arg(input,start)
            translation+=arg[0]
            translation+=delim
            start=arg[1]
        return (translation,start)

    def dollar(self,input,start):
        '''Handles dollars, either ignoring or removing them.
    
        Returns touple.'''
        if (self.remove_dollars):
            translation=""
        else:
            translation="$"
        return (translation, start)


def get_arg(input,start):
    '''Returns the argument of a latex command, starting at start.
        
    Returns a touple containing the contents of the argument
    and the index of the next character after the argument.'''
    i=start
    #Skip space
    while input[i]==" " and i < len(input):
        i+=1
    #Handle unbraced LaTeX commands
    if input[i] == "\\":
        match=latex_command.match(input[i:])
        if (match):
            arg=match.group()
            i+=len(arg)
        else:
            arg="\\"
            i+=1
        return (arg,i)
    if input[i] != "{":
        return (input[i],i+1)
    else:
        i+=1
        start=i
        j=1 #Variable to track nested braces
        while (j != 0) and i < len(input):
            if input[i] == "{":
                j+=1
            if input[i] == "}":
                j-=1
            i+=1
        #This is a hack to avoid problems when the braces haven't yet been closed
        if input[i-1]!="}":
            i+=1
        return(input[start:i-1],i)


