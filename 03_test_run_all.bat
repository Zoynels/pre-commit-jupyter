robocopy  "notebooks" "notebooks_test" "test.ipynb.sample" /is /it
cd notebooks_test
move /y "test.ipynb.sample" "test.ipynb"
cd ..

git add notebooks_test/test.ipynb
pre-commit run --verbose --all-files

pause
