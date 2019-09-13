How to Contribute to Log Anomaly Detector
=========================================

We'd love your help!

Log Anomaly Detector is GPL 3.0 License and accepts contributions via GitHub pull requests. This document outlines some of the conventions on development workflow, commit message formatting, contact points and other resources to make it easier to get your contribution accepted. We will refer to log anomaly detector as LAD for short.
We gratefully welcome improvements to documentation as well as to code.



Making a Change
---------------

Before making any significant changes, please open an issue. Each issue should describe the following:

	* Requirement - what kind of business use case are you trying to solve?
	* Problem - what missing feature in this project blocks you from solving the requirement?
	* Proposal - what do you suggest to solve the problem or improve the existing situation?
	* Any open questions to address

Discussing your proposed changes ahead of time will make the contribution process smooth for everyone. Once the approach is agreed upon, make your changes and open a pull request (PR). It is ideal to look at already open issues and start working from there. Each PR should describe:

	* Which problem it is solving. Normally it should be simply a reference to the corresponding issue, e.g. Fixes #123.
	* What changes are made to achieve that.

Your pull request is most likely to be accepted if each commit:

	* Has a good commit message. In summary:
		- Separate subject from body with a blank line
		- Limit the subject line to 50 characters
		- If it is a feature that it provides a one line sentence of what the feature adds to the project
		- Describes what your are fixing
		- Wrap the body at 72 characters
		- Use the body to explain what and why instead of how

Style Guide
-----------

	*  We follow the pip8 coding style guide with slight modification to line length. Please review it here:
		- https://www.python.org/dev/peps/pep-0008/

Code Linting
------------

	*  You should run coala to validate that your code is passing the code quality checks we have:

Note: You can use the following command:

`coala --ci`

To install see this documentation: http://docs.coala.io/en/latest/Users/Install.html

Branches
--------
You should have a meaningful name for your branch that your working on or reference an issue for example:
`git checkout master`
`git checkout -b issue_123`

If you ware working on issue123 then we know the history of where this pull request was requested from.

Or you can use a meanful name:

Docs1 - meaning your working on update to documentation.


Contact Points
--------------


If your curious about the project and want to know where to get started.
Look for git issues that have [good-first-issue] label.
If you would like to discuss features then reference one of the core maintainers below:


- @zmhassan - Zak Hassan

- @durandom - Marcel Hild

- @MichaelClifford  - Michael Clifford