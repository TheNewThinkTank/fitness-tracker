---
title: FastAPI v0.1.0
language_tabs:
  - javascript: javascript
  - python: python
language_clients:
  - javascript: ""
  - python: ""
toc_footers: []
includes: []
search: true
highlight_theme: darkula
headingLevel: 2

---

<!-- Generator: Widdershins v4.0.1 -->

<h1 id="fastapi">FastAPI v0.1.0</h1>

> Scroll down for code samples, example requests and responses. Select a language for code samples from the tabs above or the mobile navigation menu.

<h1 id="fastapi-default">Default</h1>

## Main Page

<a id="opIdmain_page__get"></a>

> Code samples

```javascript

const headers = {
  'Accept':'application/json'
};

fetch('/',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/', headers = headers)

print(r.json())

```

`GET /`

Returns a greeting message for the application.

> Example responses

> 200 Response

```json
null
```

<h3 id="main-page-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|

<h3 id="main-page-responseschema">Response Schema</h3>

<aside class="success">
This operation does not require authentication
</aside>

## Get Data

<a id="opIdget_data_data_get"></a>

> Code samples

```javascript

const headers = {
  'Accept':'application/json'
};

fetch('/data',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/data', headers = headers)

print(r.json())

```

`GET /data`

Show data

> Example responses

> 200 Response

```json
null
```

<h3 id="get-data-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|

<h3 id="get-data-responseschema">Response Schema</h3>

<aside class="success">
This operation does not require authentication
</aside>

## Get Dates

<a id="opIdget_dates_dates_get"></a>

> Code samples

```javascript

const headers = {
  'Accept':'application/json'
};

fetch('/dates',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/dates', headers = headers)

print(r.json())

```

`GET /dates`

Returns a list of all workout dates.

> Example responses

> 200 Response

```json
[
  "string"
]
```

<h3 id="get-dates-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|

<h3 id="get-dates-responseschema">Response Schema</h3>

Status Code **200**

*Response Get Dates Dates Get*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|Response Get Dates Dates Get|[string]|false|none|none|

<aside class="success">
This operation does not require authentication
</aside>

## Get Dates And Splits

<a id="opIdget_dates_and_splits_dates_and_splits_get"></a>

> Code samples

```javascript

const headers = {
  'Accept':'application/json'
};

fetch('/dates_and_splits',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/dates_and_splits', headers = headers)

print(r.json())

```

`GET /dates_and_splits`

Returns a dictionary of workout dates and their corresponding muscle groups.

> Example responses

> 200 Response

```json
null
```

<h3 id="get-dates-and-splits-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|

<h3 id="get-dates-and-splits-responseschema">Response Schema</h3>

<aside class="success">
This operation does not require authentication
</aside>

## Describe Workout

<a id="opIddescribe_workout_dates__date__get"></a>

> Code samples

```javascript

const headers = {
  'Accept':'application/json'
};

fetch('/dates/{date}',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/dates/{date}', headers = headers)

print(r.json())

```

`GET /dates/{date}`

Returns a dictionary describing the workout for the given date.

<h3 id="describe-workout-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|date|path|string|true|none|

> Example responses

> 200 Response

```json
null
```

<h3 id="describe-workout-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<h3 id="describe-workout-responseschema">Response Schema</h3>

<aside class="success">
This operation does not require authentication
</aside>

## Show Exercise

<a id="opIdshow_exercise__date__exercises__exercise__get"></a>

> Code samples

```javascript

const headers = {
  'Accept':'application/json'
};

fetch('/{date}/exercises/{exercise}',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/{date}/exercises/{exercise}', headers = headers)

print(r.json())

```

`GET /{date}/exercises/{exercise}`

Returns a list of sets and reps for the given exercise and date.

<h3 id="show-exercise-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|exercise|path|string|true|none|
|date|path|string|true|none|

> Example responses

> 200 Response

```json
[
  {}
]
```

<h3 id="show-exercise-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<h3 id="show-exercise-responseschema">Response Schema</h3>

Status Code **200**

*Response Show Exercise  Date  Exercises  Exercise  Get*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|Response Show Exercise  Date  Exercises  Exercise  Get|[object]|false|none|none|

<aside class="success">
This operation does not require authentication
</aside>

# Schemas

<h2 id="tocS_HTTPValidationError">HTTPValidationError</h2>
<!-- backwards compatibility -->
<a id="schemahttpvalidationerror"></a>
<a id="schema_HTTPValidationError"></a>
<a id="tocShttpvalidationerror"></a>
<a id="tocshttpvalidationerror"></a>

```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}

```

HTTPValidationError

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|detail|[[ValidationError](#schemavalidationerror)]|false|none|none|

<h2 id="tocS_ValidationError">ValidationError</h2>
<!-- backwards compatibility -->
<a id="schemavalidationerror"></a>
<a id="schema_ValidationError"></a>
<a id="tocSvalidationerror"></a>
<a id="tocsvalidationerror"></a>

```json
{
  "loc": [
    "string"
  ],
  "msg": "string",
  "type": "string"
}

```

ValidationError

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|loc|[anyOf]|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|msg|string|true|none|none|
|type|string|true|none|none|

