
# What Sticks 11 Web
![What Sticks Logo](https://what-sticks.com/website_images/wsLogo180noName.png)
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


## Folder Structure
```
.
├── README.md
├── app_package
│   ├── __init__.py
│   ├── _common
│   │   ├── config.py
│   │   └── utilities.py
│   ├── bp_admin
│   │   ├── routes.py
│   │   └── utils.py
│   ├── bp_error
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── bp_main
│   │   └── routes.py
│   ├── bp_users
│   │   ├── routes.py
│   │   └── utils.py
│   ├── static
│   │   ├── additional_styling
│   │   ├── css
│   │   └── scss
│   └── templates
│       ├── _layout.html
│       ├── admin
│       ├── blog
│       ├── errors
│       ├── main
│       ├── modals
│       └── users
└── run.py
```
