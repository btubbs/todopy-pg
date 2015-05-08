#!/bin/bash

# If you provide any command line argument to this script it will run in "dev
# mode", which means:
# 1. Some prod-specific cleanup is skipped, like removing the setuid bit from
#    all binaries.
# 2. Some dev-specific packages will be installed, like Supervisor, Postgres,
#    etc.
export DEV_ENV=$1

echo -e "BEGINNING PRODUCTION-SPECIFIC PROVISIONING"

exec 2>&1
set -e
set -x

export PATH

cat > /etc/apt/sources.list <<EOF
deb http://archive.ubuntu.com/ubuntu trusty main
deb http://archive.ubuntu.com/ubuntu trusty-security main
deb http://archive.ubuntu.com/ubuntu trusty-updates main
deb http://archive.ubuntu.com/ubuntu trusty universe
EOF

###################
# PROD: APT DEPS
###################

apt-get update
apt-get install -y --force-yes \
    autoconf \
    bind9-host \
    bison \
    build-essential \
    coreutils \
    curl \
    daemontools \
    dnsutils \
    ed \
    git \
    graphviz \
    imagemagick \
    iputils-tracepath \
    language-pack-en \
    libbz2-dev \
    libcap-dev \
    libcurl3-dev \
    libcurl4-openssl-dev \
    libevent-dev \
    libffi-dev \
    libglib2.0-dev \
    libjpeg-dev \
    libldap2-dev \
    libltdl7 \
    libmagickwand-dev \
    libmysqlclient-dev \
    libncurses5-dev \
    libpcre3-dev \
    libpq-dev \
    libpq5 \
    libreadline6-dev \
    libsasl2-dev \
    libssl-dev \
    libxml2-dev \
    libxslt-dev \
    libyaml-0-2 \
    libyaml-dev \
    libzmq-dev \
    netcat-openbsd \
    openssh-client \
    openssh-server \
    python \
    python-dev \
    python3-dev \
    r-base-dev \
    r-mathlib \
    ruby \
    ruby-dev \
    socat \
    syslinux \
    tar \
    telnet \
    zip \
    zlib1g-dev \
    #

# https://github.com/docker/docker/issues/963
apt-get install -y --force-yes --no-install-recommends default-jdk

# language packs are usually installed on cedarish, but Ubuntu's been lazy
# about updating their dependencies, leading to things like https://paste.yougov.net/0Tf1g
# comment them out for now.
#apt-cache search language-pack \
    #| cut -d ' ' -f 1 \
    #| grep -v '^language\-pack\-\(gnome\|kde\)\-' \
    #| grep -v '\-base$' \
    #| xargs apt-get install -y --force-yes --no-install-recommends

###################
# PROD: CLEANUP
###################
if [ -z "$DEV_ENV" ]; then
    echo -e "\nDEV_ENV not set. Doing production cleanup"
    cd /
    rm -rf /var/cache/apt/archives/*.deb
    rm -rf /root/*
    rm -rf /tmp/*

    # remove SUID and SGID flags from all binaries
    function pruned_find() {
      find / -type d \( -name dev -o -name proc \) -prune -o $@ -print
    }

    # Once you do this, sudo is disabled.
    pruned_find -perm /u+s | xargs -r chmod u-s
    pruned_find -perm /g+s | xargs -r chmod g-s

    # remove non-root ownership of files
    chown root:root /var/lib/libuuid

    set +x
    echo -e "\nRemaining suspicious security bits:"
    (
      pruned_find ! -user root
      pruned_find -perm /u+s
      pruned_find -perm /g+s
      pruned_find -perm /+t
    ) | sed -u "s/^/  /"
else
    echo -e "\nDEV_ENV set. Skipping production cleanup"
fi

echo -e "\nInstalled versions:"
(
  git --version
  ruby -v
  gem -v
  python -V
) | sed -u "s/^/  /"

echo -e "\nFINISHED PRODUCTION-SPECIFIC PROVISIONING"

if [ $DEV_ENV ] ; then
echo -e "\nBEGINNING DEV-SPECIFIC PROVISIONING"

#######################
# DEV: BASIC/MISC STUFF
#######################

pip install \
    mercurial \
    virtualenv \
    virtualenvwrapper \
    #

# Set root passwd in VM so VR workers can SSH in.
echo  "root:vagrant" | chpasswd

cat > /etc/hosts <<EOF
127.0.0.1 localhost vagrant-ubuntu-trusty-64

# The following lines are desirable for IPv6 capable hosts
::1 ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
ff02::3 ip6-allhosts
EOF

#######################
# DEV: PACKAGES
#######################

# Keep this package list alphabetized
apt-get install -y --force-yes \
    htop \
    python-pip \
    python-setuptools \
    python-software-properties \
    vim \
    #

gem install foreman

#######################
# DEV: ~/.bashrc
#######################

cat > /home/vagrant/.bashrc <<EOF
case \$- in
    *i*) ;;
      *) return;;
esac

HISTCONTROL=ignoreboth

shopt -s histappend

HISTSIZE=1000
HISTFILESIZE=2000

shopt -s checkwinsize

[ -x /usr/bin/lesspipe ] && eval "\$(SHELL=/bin/sh lesspipe)"

if [ -z "\${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=\$(cat /etc/debian_chroot)
fi

case "\$TERM" in
    xterm-color) color_prompt=yes;;
esac

#force_color_prompt=yes

if [ -n "\$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
    color_prompt=yes
    else
    color_prompt=
    fi
fi

if [ "\$color_prompt" = yes ]; then
    PS1='\${debian_chroot:+(\$debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\\$ '
else
    PS1='\${debian_chroot:+(\$debian_chroot)}\u@\h:\w\\$ '
fi
unset color_prompt force_color_prompt

case "\$TERM" in
xterm*|rxvt*)
    PS1="\[\e]0;\${debian_chroot:+(\$debian_chroot)}\u@\h: \w\a\]\$PS1"
    ;;
*)
    ;;
esac

if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "\$(dircolors -b ~/.dircolors)" || eval "\$(dircolors -b)"
    alias ls='ls --color=auto'
    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

alias alert='notify-send --urgency=low -i "\$([ \$? = 0 ] && echo terminal || echo error)" "\$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert\$//'\'')"'

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi

export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python2.7
source /usr/local/bin/virtualenvwrapper.sh
EOF
# end /home/vagrant/.bashrc

###################
# DEV: POSTGRES
###################
cat > /etc/apt/sources.list.d/pgdg.list <<EOF
deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main
EOF

wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | \
  apt-key add -
apt-get update

apt-get install -y --force-yes \
    postgresql-9.4 \
    postgresql-server-dev-9.4 \
    postgresql-contrib-9.4 \
    #

cat > /etc/postgresql/9.4/main/pg_hba.conf <<EOF
local   all             postgres                                trust
local   all             all                                     trust
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
local   replication     postgres                                trust
EOF


cat > /etc/postgresql/9.4/main/postgresql.conf <<EOF
data_directory = '/var/lib/postgresql/9.4/main'
hba_file = '/etc/postgresql/9.4/main/pg_hba.conf'
ident_file = '/etc/postgresql/9.4/main/pg_ident.conf'
external_pid_file = '/var/run/postgresql/9.4-main.pid'
port = 5432
max_connections = 100
unix_socket_directories = '/var/run/postgresql'
ssl = true
ssl_cert_file = '/etc/ssl/certs/ssl-cert-snakeoil.pem'
ssl_key_file = '/etc/ssl/private/ssl-cert-snakeoil.key'
shared_buffers = 128MB
# dynamic_shared_memory_type = posix
log_line_prefix = '%t [%p-%l] %q%u@%d '
log_timezone = 'UTC'
stats_temp_directory = '/var/run/postgresql/9.4-main.pg_stat_tmp'
datestyle = 'iso, mdy'
timezone = 'UTC'
lc_messages = 'en_US.UTF-8'
lc_monetary = 'en_US.UTF-8'
lc_numeric = 'en_US.UTF-8'
lc_time = 'en_US.UTF-8'
default_text_search_config = 'pg_catalog.english'
EOF

service postgresql restart
set +e
createuser -U postgres --superuser vagrant
createdb -U postgres --owner=vagrant vagrant
set -e

###################
# DEV: CLEANUP
###################
# Vagrant has Puppet and Chef in all boxes by default.  Clean them out.
apt-get remove -y --force-yes \
    chef \
    puppet \
    #
apt-get autoremove -y --force-yes

echo -e "\nFINISHED DEV-SPECIFIC PROVISIONING"
fi
exit 0


