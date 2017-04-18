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
   			"success": true,
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
		
		
		
### Organizations

_/orgs_

* POST ~ Create an org, expects JSON like:

		REQUIRED: JWT
		REQUEST:
		{
			"user_id": "26e63eaf-34e3-4265-a20f-eecdfb8ab6e1",
			"name": "The Association for Birdlike Peoples"
		}
		
		RESPONSE:
		{
    		"org_id": "fc64c155-5f74-492b-ba59-8f3455d3a15e",
    		"success": true,
   		 	"user_id": "26e63eaf-34e3-4265-a20f-eecdfb8ab6e1"
		}
		
		
* GET ~ Get a list of orgs:

		REQUIRED: JWT	
     	RESPONSE:
     	{
    		"count": 1,
   			"orgs": [
        	{
	            "created": null,
	            "email": null,
	            "fiveoone": null,
	            "id": "fc64c155-5f74-492b-ba59-8f3455d3a15e",
	            "location_id": null,
	            "mission": null,
	            "name": "The Association for Birdlike Peoples",
	            "phone": null,
	            "premium": null,
	            "registered": null,
	            "services": null
        	}]
        }       
       

