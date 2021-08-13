## IBB game tracker app

It is a reminder service for the service of Istanbul Metropolitan Municipality where you can rent a sport field online. <br><br>It uses e-mail as a reminder tool. I will try to automate it as much as I can(possibly an UI for collecting user applications).

`.env variable explanations;`
<br> ACTION => Should be a valid option "ADD_TO_BASKET" or "WARN". <br>
 ``warn option just sends mail, add to basket locks requested game to cart for 12h and sends mail about it.``
<br> GAME_ID => Select option name field's value for particular sport.
<br> FACILITY_ID =>  Select option name field's value for particular facility.
<br> PITCH_ID => Select option name field's value for particular pitch.
<br> REQUESTED_TIME_RANGE => Should be a valid option for selected pitch.
<br> RECEIVER_EMAILS => use a comma and space after comma for each email, if there is 1 email don't use email or space. 
