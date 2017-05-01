# AIDEX API

### Users

_/users_

* POST ~ Create a users, expects JSON like:

		REQUEST:
		{
		   	"name": "Pernaculus Ortoculus",
			"password": "password",
			"email": "pculortolus@culuc.com",
			"phone": "787-455-5444"
		}

		RESPONSE:
		{
    		"user_id": "26e63eaf-34e3-4265-a20f-eecdfb8ab6e1"
		}


_/auth_

* POST ~ Authenticate a user and recieve a JWT, expects JSON like:

		REQUEST:
		{
			"email": "pculortolus@culuc.com",
			"password": "password"
		}

		RESPONSE:
		{
			"access_token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE0OTI0NzI5NzgsImlhdCI6MTQ5MjQ3MjY3OCwibmJmIjoxNDkyNDcyNjc4LCJpZGVudGl0eSI6IjI2ZTYzZWFmLTM0ZTMtNDI2NS1hMjBmLWVlY2RmYjhhYjZlMSJ9.9suLDK-HUxVY82u75Dav9jI4JhFChiYK-51qwaavNPo"
		}

_/organized/orgs_

* GET ~ Get the orgs a user organizes

		REQUIRED: JWT, user_id
		REQUEST: {"user_id": {"type": "string"}
		RESPONSE:      	RESPONSE:
     	{
   			"orgs": [{
	            "email": null,
	            "fiveoone": null,
	            "id": "fc64c155-5f74-492b-ba59-8f3455d3a15e",
	            "locations": [{
					"id": 1,
					"address": "blah",
					"org_id": "blah",
					"event_id": "blah",
					"country": "blah",
					"city": "blah"
				}],
	            "mission": "To protect the interests of birdlike peoples",
	            "name": "The Association for Birdlike Peoples",
	            "phone": "4444444444",
	            "premium": True,
	            "registered": null,
	            "services": ["blah", ..."],
				"established": "blah",
				"categories" ["blah", ...]
        	}],
        }

### Organizations

_/orgs_

* POST ~ Create an org, expects JSON like:

		REQUIRED: JWT, user_id, name, locations, categories
		REQUEST:
					{
			"user_id": {"type": "string"},
            "name": {"type": "string"},
            "email": {"type": "string"},
            "fiveoone": {"type": "string"},
            "phone": {"type": "string"},
            "mission": {"type": "string"},
            "services": {
                "type": "array",
                "items": {
                    "type": "string"
                }},
			"categories": {
                "type": "array",
                "items": {
                    "type": "string"
				}},
            "established": {"type": "string"},
            "locations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "address": {"type": "string"},
                        "city": {"type": "string"},
                        "country": {"type": "string"},
                    }}
            }

		RESPONSE:
		{
    		"org_id": "fc64c155-5f74-492b-ba59-8f3455d3a15e",
   		 	"user_id": "26e63eaf-34e3-4265-a20f-eecdfb8ab6e1"
		}


* GET ~ Get an org and their events:

		REQUIRED: JWT
     	RESPONSE:
     	{
   			"org": {
	            "email": null,
	            "fiveoone": null,
	            "id": "fc64c155-5f74-492b-ba59-8f3455d3a15e",
	            "locations": [{
					"id": 1,
					"address": "blah",
					"org_id": "blah",
					"event_id": "blah",
					"country": "blah",
					"city": "blah"
				}],
	            "mission": "To protect the interests of birdlike peoples",
	            "name": "The Association for Birdlike Peoples",
	            "phone": "4444444444",
	            "premium": True,
	            "registered": null,
	            "services": ["blah", ..."],
				"established": "blah",
				"categories" ["blah", ...]
        	},
			"events" : [{
				"id": "blah",
				"name": "blah",
				"timestamp"
			}]
        }

* PUT - Update an org:

		REQUIRED: JWT ["org_id", "user_id"]
		REQUEST: Same as post
		RESPONSE: Same as post


_/follow_

* POST ~ Follow an org:

		REQUIRED: JWT ["org_id", "user_id"]
		REQUEST: {
            "user_id": {"type": "string"},
            "org_id": {"type": "string"}},
		RESPONSE: {
			"user_id": "blah",
			"org_id": "blah"}

_/following_

* GET ~ Get the orgs a user is following

		REQUIRED: JWT ["user_id"]
		REQUEST: {
            "user_id": {"type": "string"}}
		RESPONSE: {
			"user_id": "blah",
			"followed_orgs": [{
	            "email": null,
	            "fiveoone": null,
	            "id": "fc64c155-5f74-492b-ba59-8f3455d3a15e",
	            "locations": [{
					"id": 1,
					"address": "blah",
					"org_id": "blah",
					"event_id": "blah",
					"country": "blah",
					"city": "blah"
				}],
	            "mission": "To protect the interests of birdlike peoples",
	            "name": "The Association for Birdlike Peoples",
	            "phone": "4444444444",
	            "premium": True,
	            "registered": null,
	            "services": ["blah", ..."],
				"established": "blah",
				"categories" ["blah", ...]
        	}, ...]

_/unfollow_

* POST ~ Unfollow an org

		REQUIRED: JWT ["org_id", "user_id"]
		REQUEST: {
            "user_id": {"type": "string"},
            "org_id": {"type": "string"}}
		RESPONSE: {
			"user_id": "blah",
			"org_id": "blah"}

_/followers_

* GET - Get an orgs followers

		REQUIRED: JWT ["org_id", "user_id"]
		REQUEST: {
            "user_id": {"type": "string"},
            "org_id": {"type": "string"}}
		RESPONSE: {
			"followers": [{
		   		"name": "Pernaculus Ortoculus",
				"user_id": "blah",
				"email": "pculortolus@culuc.com",
				"phone": "787-455-5444"
			}
			"org_id": "blah"}

### Events

_/events_

* POST ~ Create an event

		REQUIRED: JWT, ["org_id", "location", "start_date", "end_date", "name", "user_id"]
		REQUEST: {
			"org_id": {"type": "string"},
            "user_id": {"type": "string"},
            "event_id": {"type": "string"},
            "name": {"type": "string"},
            "start_date": {"type": "string"},
            "end_date": {"type": "string"},
            "location": {
                "type": "object",
                "properties": {
                    "address": {"type": "string"},
                    "city": {"type": "string"},
                    "country": {"type": "string"},
                }
		}
		RESPONSE: {"event_id": event.id}


* PUT ~ Update an event

		REQUIRED: JWT, ["org_id", "event_id", "user_id"]
		REQUEST: same as post
		RESPONSE: same as post


* GET - Get an event

		REQUIRED: JWT, ["event_id"]
		REQUEST: {"event_id": {"type": "string"}}
		RESPONSE: {
			"id": "blah",
			"org_id": "blah",
			"start_date": "01/24/2412T12:30:25",
			"end_date": "01/24/2412T12:30:26",
			"timestamp": "01/22/2412T12:30:25"
			"location": {
				"id": 1,
				"address": "blah",
				"org_id": "blah",
				"event_id": "blah",
				"country": "blah",
				"city": "blah"
			}


_/attend_

* POST ~ Attend an event

		REQUIRED: JWT, ["user_id", "event_id"]
		REQUEST: {
		"user_id": {"type": "string"},
		"event_id": {"type": "string"}}
		RESPONSE: {
			"user_id": "blah",
			"event_id": "blah",
			"review": "",
			"as_volunteer": False,
		}

_/unattend_

* POST ~ Unattend an event: Same as _/attend_

_/volunteer_

* POST ~ Volunteer an attended event: Same as _/attend_

_/unvolunteer_

* POST ~ Unvolunteer an attended event: Same as _/attend_

_/attendees_

* GET ~ Get the attendees of an event (includes volunteers)

		REQUIRED: JWT, ["org_id", "user_id", "event_id"]
		REQUEST: {
            "org_id": {"type": "string"},
            "user_id": {"type": "string"},
            "event_id": {"type": "string"}
            }
		RESPONSE: {
			"event_id": "blah",
			"attendees": [{
		   		"name": "Pernaculus Ortoculus",
				"user_id": "blah",
				"email": "pculortolus@culuc.com",
				"phone": "787-455-5444"
			}, ...]

_/volunteers_

* GET ~ Get the volunteers of an event

		REQUIRED: JWT, ["org_id", "user_id", "event_id"]
		REQUEST: {
            "org_id": {"type": "string"},
            "user_id": {"type": "string"},
            "event_id": {"type": "string"}
            }
		RESPONSE: {
			"event_id": "blah",
			"volunteers": [		{
		   		"name": "Pernaculus Ortoculus",
				"user_id": "blah",
				"email": "pculortolus@culuc.com",
				"phone": "787-455-5444"
			}, ...]


_/reviews_

* POST ~ Post a review about a user's volunteership at an event

		REQUIRED: JWT, ["org_id", "user_id", "event_id", "review"]
		REQUEST:  {
            "org_id": {"type": "string"},
            "user_id": {"type": "string"},
            "event_id": {"type": "string"},
            "review": {"type": "string"}
            }
		RESPONSE: {
			"user_id": "blah",
			"event_id": "blah",
			"review": "blah"}

* GET ~ Get the reviews for a user

		REQUIRED: JWT, ["user_id", "org_id"]
		REQUEST: {
			"user_id": {"type": "string"},
			"org_id": {"type": "string"}}
		RESPONSE: {
			"user_id": "blah",
			"reviews": ["great", "meh", ...]


_/attendances_

* GET ~ Get the events a user is attending, only pending ones if "active" is `True`

		REQUIRED: JWT, ["user_id"]
		REQUEST: {
			"user_id": {"type": "string"},
            "active": {"type": "boolean"}}
		RESPONSE: {
			"user_id": "blah",
			"attendances": [{
			{
			"id": "blah",
			"org_id": "blah",
			"start_date": "01/24/2412T12:30:25",
			"end_date": "01/24/2412T12:30:26",
			"timestamp": "01/22/2412T12:30:25"
			"location": {
				"id": 1,
				"address": "blah",
				"org_id": "blah",
				"event_id": "blah",
				"country": "blah",
				"city": "blah"
			}}}]


### Search

_/search_

		REQUIRED: JWT
		REQUEST: {
            "keywords": {
                "type": "array",
                "items": {
                    "type": "string"
                }},
            "categories": {
                "type": "array",
                "items": {
                    "type": "string",
                }},
            "cities": {
                "type": "array",
                "items": {
                    "type": "string"
                }},
            "country": {"type": "string"},
            "limit": {"type": "integer"},
            "page": {"type": "integer"}},
		RESPONSE: {
            "count": 1,
            "matches": [{
	            "email": null,
	            "fiveoone": null,
	            "id": "fc64c155-5f74-492b-ba59-8f3455d3a15e",
	            "locations": [{
					"id": 1,
					"address": "blah",
					"org_id": "blah",
					"event_id": "blah",
					"country": "blah",
					"city": "blah"
				}],
	            "mission": "To protect the interests of birdlike peoples",
	            "name": "The Association for Birdlike Peoples",
	            "phone": "4444444444",
	            "premium": True,
	            "registered": null,
	            "services": ["blah", ..."],
				"established": "blah",
				"categories" ["blah", ...]
        	}],
            "page": 1}
