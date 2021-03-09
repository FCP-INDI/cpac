(head -n $(read -d : <<< $(less README.rst | grep ".. BEGIN USAGE" -n); expr $REPLY + 1) README.rst; \
printf ".. code-block:: shell\n\n    cpac --help\n"; \
cpac --help | sed 's/^/    /'; \
tail --lines=+$(read -d : <<< $(less README.rst | grep ".. END USAGE" -n); expr $REPLY - 1) README.rst\
) > tempREADME &&
mv tempREADME README.rst &
wait %1

if [[ $(git diff --numstat README.rst) ]]; then
    git add README.rst
    git commit -m ":memo: Update usage from helpstring"
    git push origin HEAD:${GITHUB_REF}
fi

exit 0