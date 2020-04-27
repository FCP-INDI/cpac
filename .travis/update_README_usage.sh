(head -n $(read -d : <<< $(less README.rst | grep ".. BEGIN USAGE" -n); expr $REPLY + 1) README.rst; \
printf ".. code-block:: shell\n\n    cpac --help\n"; \
cpac --help | sed 's/^/    /'; \
tail --lines=+$(read -d : <<< $(less README.rst | grep ".. END USAGE" -n); expr $REPLY - 1) README.rst\
) > tempREADME &&
mv tempREADME README.rst &
wait %1

if [[ $(git diff --numstat README.rst) ]]; then
    OLD_ORIGIN=$(git remote get-url origin)
    git remote set-url origin $"https://${GITHUB_USERNAME}:${GITHUB_PUSH_TOKEN}@github.com/"${OLD_ORIGIN:19}
    git add README.rst
    git commit -m ":books: Update usage from helpstring" -m "[skip travis]"
    git push origin HEAD:$TRAVIS_BRANCH
fi