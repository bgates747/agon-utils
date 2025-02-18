hello!

this package contains some building bricks for a compression program.
The files are distributed with GNU general public license.

for more IMPORTANT readme information please see the end of this file.

having done this legalize stuff, here for the fun part :)

Contained herein is:

a) an entropy coder (range coder) similar to arithmetic coding with
   high operation speed. More info on the homepage (see end)
   files: rangecod.h, rangecod.c

b) a fast probability model (qsmodel) doing periodic updates of
   probability and keeping the total count a power of two. It is
   used in two of the example programs.
   files: qsmodel.h, qsmodel.c

c) a simple sample compression program with count modelling
   files: simple_c.c simple_d.c

d) a simple sample compression program with order 0 adaptive
   probability modelling using qsmodel.
   files: comp.c decomp.c

e) a simple sample compression program with order 1 adaptive
   probability modelling using qsmodel.  Compare this program with
   comp to see I just changed the modelling, not the coding.
   files: comp1.c decomp1.c

f) a debugging range coder; this coder expands files but
   stores explicit information about parameters passed to
   rangecoder. It has exactly the same interface as rangecod.c
   so just replace.  This coder is handy if you can't decode
   correctly, it will help you locate the problem in your model.
   files: dummycod.c

g) auxiliary file containing definitions used: port.h

h) text files:
   readme.txt: this file
   examples.txt: more information about the examples
   license: GNU general public license, version 2.
   makefile: makefile to build examples.

reliability information: qsmodel and rangecoder are used in szip;
several hunderd GB (including testsets) were handled sucessfully.
I do not have a 16-bit compiler any more and there were some
problems with rangecoder 1.1 on these (things like "0xff<<23"
which of course now reads "(code_value)0xff<<23".
qsmodel assumes int's to be able to hold frequency counts;
so be careful on 16-bit computers.


There is a supplimentary file called renorm95.c distributed under
different conditions (basically: research purposes) that changes
the rangecoder into an arithmetic coder to allow comparisons.
It can be downloaded from the homepage (see below). Note that these
programs differ in the closing from the ones used to produce the
tables for my DCC98 poster "Data Compression Conference, March 1998,
Snowbird, Utah: M. Schindler: A fast Renormalisation for Arithmetic
Coding" so filesize does vary by some bytes.

contact:
michael@compressconsult.com
http://www.compressconsult.com/rangecoder/



IMPORTANT LEGAL STUFF:
These programs are distributed with the GNU general public license.
here is a quote:

>2.  b) You must cause any work that you distribute or publish, that in
>    whole or in part contains or is derived from the Program or any
>    part thereof, to be licensed as a whole at no charge to all third
>    parties under the terms of this License.
If this doesn't fit your needs (free of charge, availability of source
code) email me, I am sure we can arrange. Politics: if you charge I
charge - but less than you need to hire a programmer to write & test it.
I will not warrant more than your employee would when writing such a
program even if I charge.


another qote (No known bugs, but nevertheless):
>  11. BECAUSE THE PROGRAM IS LICENSED FREE OF CHARGE, THERE IS NO WARRANTY
>FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW.  EXCEPT WHEN
>OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES
>PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED
>OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
>MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.  THE ENTIRE RISK AS
>TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU.  SHOULD THE
>PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING,
>REPAIR OR CORRECTION.
>
>  12. IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
>WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR
>REDISTRIBUTE THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES,
>INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING
>OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED
>TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY
>YOU OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER
>PROGRAMS), EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE
>POSSIBILITY OF SUCH DAMAGES.

Another warning just to make sure you know the following:
Compression is about removing redundancy from data, so an error on the
compressed data has a larger effect than an error on the raw data.
Whenever you use these programs or derive other works from them
make sure to do a periodic restart of the coder and the model - only
such restarts allow resyncronisation of encoder and decoder after a
data error. Example: If you use comp on a tar-file of a whole disk and
suffer a data error everything in the tar-file after the error is lost;
none of the usage examples here does restart.
