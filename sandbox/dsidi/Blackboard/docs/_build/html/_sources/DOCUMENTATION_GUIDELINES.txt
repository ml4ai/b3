##################################
Draconian Documentation Guidelines
##################################

**************
Best Practices
**************

Rather than maintain separate documentation both in the source and externally,
we are using `Sphinx <http://sphinx-doc.org/>`_. This requires almost nothing of us, but here are a few
tips and practices that will help make our laziness more elegant:

* indentation is significant in the documentation. Paragraphs are at the
  same indent level, and separated by a blank line, etc.
  
* You can use `reST <http://sphinx-doc.org/rest.html#rst-primer>`_ for 
  *impressive* bragging rights at the bar:

   * \:param str p1\: great parameter here
   * \:return\: result
   * \:rtype\: int
   * \:raises TypeError\: if blah blah happens

* for module data members and class attributes, use docstrings only *below* 
  the thing they are documenting, or use '#:' to comment *above*

* document as you write, so that the documentation evolves with the code

********
Updating
********

* to update the documentation, just go to the doc directory and do
  ``make html``


