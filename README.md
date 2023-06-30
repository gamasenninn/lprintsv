# lprintsv
label print server  

it needs ba400 server.  
This is the front end of the ba400 server.  
Connect to ba400 server and output DB data.

## quasar
```
cd front/quasar-app
quasar dev
```

## Swagger
```
cd app
http://localhost:8000/docs
```

## Notes on Deployment

- /convert is the process of converting data from an arbitrary DB.  
This is different for each user, so if you do not implement it, comment it out from the import of the main app.  
If you do not implement it, comment it out from the import of the main app.  
- /app/sql_app.db is in the test environment. If you want to use it in production, copy it from the test environment or create a new one in the production environment.
- After you have finished testing spa or electron in /front/quasar-app/dist/ in the development environment, copy the necessary portion to the production environment.