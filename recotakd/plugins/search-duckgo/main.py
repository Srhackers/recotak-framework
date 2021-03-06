import sys
import time
# Copyright (c) 2014, curesec GmbH
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this list of 
# conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice, this list 
# of conditions and the following disclaimer in the documentation and/or other materials 
# provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its contributors may be used 
# to endorse or promote products derived from this software without specific prior written 
# permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS 
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF 
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE 
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR 
# TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, 
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import logging
import threading
import duckgo
import ccdClasses as ccd

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def main(dbh, args):
    logger.debug("starting plugin %s" % __name__)

    # overwrite duckgo logger to send log to ccd
    duckgo.logging = logger

    duck = duckgo.DuckQuery(dbh)
    duck.parse_arguments(args)
    duck.calc_query_id(duck.query)

    event = threading.Event()
    threads = []
    duck.search()
    time.sleep(0.05)

    for _ in range(duck.thread_count):
        duck_thread = duckgo.DuckQuery(dbh, event)
        duck_thread.setDaemon(True)
        duck_thread.output_directory = duck.output_directory
        duck_thread.set_query(duck.query)
        duck_thread.set_count(duck.count)
        duck_thread.set_query_id(duck.query_id)
        duck_thread.start()
        threads.append(duck_thread)

    for duck_thread in threads:
        duck_thread.join()


def register():
    plugin = ccd.Plugin(
        "duckgo",
        ["searchengines"],
        dbtemplate=[ccd.Tmpl.SE_LINK_CRAWLER])
    plugin.execute = main
    return plugin


if __name__ == '__main__':
    main(None, sys.argv[1:])
