@echo off
echo Installing pgvector for PostgreSQL 18...
copy /Y "%TEMP%\vector_pg18\lib\vector.dll" "C:\Program Files\PostgreSQL\18\lib\"
copy /Y "%TEMP%\vector_pg18\share\extension\vector*" "C:\Program Files\PostgreSQL\18\share\extension\"
if not exist "C:\Program Files\PostgreSQL\18\include\server\extension\vector" mkdir "C:\Program Files\PostgreSQL\18\include\server\extension\vector"
copy /Y "%TEMP%\vector_pg18\include\server\extension\vector\*" "C:\Program Files\PostgreSQL\18\include\server\extension\vector\"
echo.
echo pgvector files copied successfully!
pause
