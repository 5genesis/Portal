**16/07/2021** [Version 2.4.5]

 - Fix network services onboarding
 - Remove 'Core' location

*Update notes*:
- This release includes database changes. When updating from a previous version ensure that you
run the `flask db upgrade` command over the activated Portal virtualenv

**24/06/2021** [Version 2.4.4]

 - Add generic 'Core' location
 - Update Flask-moment dependency

*Update notes*:
- In case of issues with the rendering of dates or exceptions related to `moment` or `Flask-moment`,
re-run `pip install -r requirements.txt` over the activated Portal virtualenv.

**08/06/2021** [Version 2.4.3]

 - Add 'None' as selectable scenario

**22/04/2021** [Version 2.4.2]

 - Analytics Dashboard integration

**12/01/2021** [Version 2.4.1]

 - Updated documentation

**22/12/2020** [Version 2.4.0]

 - Added East/West interface
 - Added support for distributed experiment creation/visualization

**31/07/2020** [Version 2.3.4]

 - Added Base Slice and Scenario to experiment creation

**14/07/2020** [Version 2.3.3]

 - Added experiment descriptor retrieval

**10/07/2020** [Version 2.3.2]

 - Updated NS handling

**29/06/2020** [Version 2.3.1]

 - Add reservation time to MONROE experiments
 - Bugfixes

**13/05/2020** [Version 2.3.0]

 - Available TestCases and UEs are now retrieved from the ELCM
 - Per user custom test cases
 - Improved custom test case parameters interface

**15/04/2020** [Version 2.2.0]

 - Custom and MONROE experiment types
 - Updated experiment descriptor

**13/04/2020** [Version 2.1.0]

 - Onboarding of network services using Dispatcher

**16/03/2020** [Version 2.0.0]

 - Use Dispatcher for user authentication
 - Added customizable platform information page
 - Added experiment result download
 - Hide VNF/NS functionality

**31/10/2019** [Version 1.1.1]

 - Avoid exception when creating duplicated users

**02/10/2019** [Version 1.1.0]

 - Modified VNF/NS handling

**29/05/2019** [Version 1.0.8]

 - Auto-update displayed experiment execution information with values provided by the ELCM.

**24/05/2019**

 - Included link to experiment results in Grafana after experiment execution ends.

**22/05/2019**

 - Updated handling of VNF uploads.
 - Added Slice and VNF information to experiment descriptor.

**17/05/2019**

 - Added support for deleting uploaded VNFs.

**16/05/2019**

 - Initial implementation of VNF uploads.

**14/05/2019**

 - Added system-wide notices and user actions feed.
 - Improved format of displayed times.

**13/05/2019**

 - Added view for displaying experiment execution details and logs retrieved from the ELCM.

**24/04/2019**

Initial merge from UMA repository

 - User registration
 - Experiment creation and execution
 - Execution history
