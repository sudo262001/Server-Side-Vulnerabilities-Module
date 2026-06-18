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
