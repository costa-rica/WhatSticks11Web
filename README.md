
# What Sticks 11 Web



## Description
Web application for What Sticks


## Features
- Users can login and download daily data files that create their correlations
- Admin data functions including backing up database and replenishing data.



## Contributing
We welcome contributions to the WhatSticks11 Web project. 


For any queries or suggestions, please contact us at nrodrig1@gmail.com.


## Documentation

### Admin

#### @bp_admin.route('/admin_db_upload_zip')
This route heavily leverages ws_utilities/web/admin.py

- Even if no new users or locations are added via df_crosswalk, .zip process will add new data that does not already exist in AppleHealth, WeatherHistory, UserLocationDay.

