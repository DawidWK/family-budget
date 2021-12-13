# family-budget

## INSTALLATION GUIDE 

1. Pull repository
2. cd to project root directory
3. `docker build .` - build docker image
4. `docker-compose up` - start services 


## ENDPOINTS

### 1. /api/users/
- /api/user/create/
  - `curl --header "Content-type: application/json" --request POST --data '{"username": "test", "password": "Password123!", "password2": "Password123!"}' http://127.0.0.1:8000/api/user/create/` - create user with username: Test, password: Password123!

- /api/user/token/
  - `curl --header "Content-type: application/json" --request POST --data '{"username": "test", "password": "Password123!"}' http://127.0.0.1:8000/api/user/token/` - Generate authorization token

- /api/user/me/
  - `curl -H "Content-type: application/json" -H "Authorization: Token a6683e9145e0aaf7718a37fbb96e9e68a77846e0" --request GET http://127.0.0.1:8000/api/user/me/` - Info about authenticated user


### 2. /api/category/
- /api/category/
  - `curl -H "Content-type: application/json" -H "Authorization: Token a6683e9145e0aaf7718a37fbb96e9e68a77846e0" --request GET http://127.0.0.1:8000/api/category` - view list of categories
- /api/category/ 
  - `curl -H "Content-type: application/json" -H "Authorization: Token a6683e9145e0aaf7718a37fbb96e9e68a77846e0"  --request POST --data '{"name": "my category"}' http://127.0.0.1:8000/api/category/` - create new category "my category"

### 3. /api/budget/
- /api/budget/` 
  - `curl -H "Content-type: application/json" -H "Authorization: Token a6683e9145e0aaf7718a37fbb96e9e68a77846e0" --request GET http://127.0.0.1:8000/api/budget/` - view list of budgets where authenticated user is an author or budget is shared with authenticated user 
- /api/budget/
  - `curl -H "Content-type: application/json" -H "Authorization: Token a6683e9145e0aaf7718a37fbb96e9e68a77846e0"  --request POST --data '{"name": "My Budget", "income": 1000.00, "expenses": 500.00, "category": 1}' http://127.0.0.1:8000/api/budget/` - creates new budget \*`category` takes PK of category item, \* `shared_with` takes list of PK's of users 


## Filtering and Pagination
- to filter budgets assigned only to authenticated user add `?assigned_only=1`
- Default pagination is set to 10 items per list, to change it add `?limit=` with limit itmes per page number
- To change offset of pagination add `?offset=` with offset number


## Tests 
- `docker-compose run --rm app sh -c "python3 manage.py test && flake8"` - run tests
