alias fly-login='fly -t v7 login'
alias extract='fly -t v7 gp -p sync-osbooks | pipemgr extract'
alias publish='fly -t v7 sp -p sync-osbooks -c sync-osbooks.yml'