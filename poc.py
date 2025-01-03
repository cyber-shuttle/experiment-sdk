#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import cybershuttle as cs
from cybershuttle import md

# -------------------------------------------------------------------------------------------------
# AUTHENTICATION

# users may have default configs (both general and app-specific)
cs.auth.login()
# this will block until device auth flow is completed

# -------------------------------------------------------------------------------------------------
# DEFINING THE EXPERIMENT

# [definition]
exp = md.NAMD.initialize(
    name="yasith_namd_experiment",
    config_file="data/pull.conf",
    pdb_file="data/structure.pdb",
    psf_file="data/structure.psf",
    other_files=[
        "data/b4pull.pdb",
        "data/b4pull.restart.coor",
        "data/b4pull.restart.vel",
        "data/b4pull.restart.xsc",
        "data/par_all36_water.prm",
        "data/par_all36_prot.prm",
    ],
)
# [replicas]
# 1 replica <==> 1 node (preferably on 1 job)

for _ in range(4):
    exp.add_replica()  # add_replica() will add a replica to exp, with DEFAULT runtime config

    # exp.add_replica(  # add_replica(runtime) will add a replica to exp, with CUSTOM runtime config
    #     runtime=cs.runtime.Remote(
    #         cluster="expanse",
    #         queue="shared",
    #         profile="grprsp1",
    #         num_cpus=8,
    #     ),
    # )

# [sweeps]
# 1 sweep instance <==> 1 job <==> 1 node
# exp.add_sweep(x=[8, 16, 32])  # this add_sweep(...) will add 3 jobs to exp: {x=8, x=16, and x=32}

# -------------------------------------------------------------------------------------------------
# PLANNING THE EXPERIMENT RUN

plan = exp.plan()  # this will create a plan for the experiment
plan.describe()  # this will describe the plan

# [saving/loading plans]
plan.save_json("plan.json")  # this will save the plan to a file
plan = cs.plan.Plan.load_json("plan.json")  # this will load the plan from a file
plan.describe()  # this will describe the plan

# [executing plans]
plan.launch()  # this will execute the plan (will ask for user confirmation)

# at this point, the plan will be sent to the runtimes for execution
# the runtimes will check if they can handle it, and throw an error if they cannot.
# if an error is thrown, the user will be notified and asked to regenerate the plan.

# [waiting for completion]
plan.join(check_every_n_mins=10)  # this will block execution until the plan is completed - don't poll
# (instead wait for callback)
# at this point the plan is completed.

# [terminating plans]
plan.stop()  # this will terminate the plan
# at this point the plan is terminated.

# -------------------------------------------------------------------------------------------------

for task in plan.tasks:
    status = task.status()
    files = task.files()
    print(status, files)

# -------------------------------------------------------------------------------------------------
# MONITORING THE RUNNING EXPERIMENT

# WHILE the job is running, users may want to analyze interim outputs, to determine if they want to
# continue the experiment or cancel it. For this, cybershuttle will start and run an AGENT app
# on possibly a different node, but WITH access to the same filesystem as the experiment.

# imports outside the function can be accessed by the agent using python session
# the agent initialization from session vars - dimuthu is handling this

from matplotlib import pyplot as plt
import pandas as pd

for task in plan.tasks:

    @cs.task_context(task)
    def visualize():
        data = pd.read_csv("data.csv")
        plt.figure(figsize=(8, 6))
        plt.plot(data["x"], data["y"], marker="o", linestyle="-", linewidth=2, markersize=6)
        plt.title("Plot for data file")

    visualize()

# -------------------------------------------------------------------------------------------------
# POST-ANALYSIS OF THE EXPERIMENT

analysis_runtime = cs.runtime.Remote(
    cluster="delta",
    queue="shared",
    profile="grprsp1",
    num_cpus=8,
)


# [collecting results]
paths = plan.collect_results(runtime=analysis_runtime)

# [analysis on VMD GUI App] ---- skipping for now
vmd = md.VMD.initialize(name="yasith_vmd_analysis")
vmd.open(runtime=analysis_runtime, location=".")

# -------------------------------------------------------------------------------------------------
# CLEANUP

cs.auth.logout()


# -------------------------------------------------------------------------------------------------
# NOTES

# Some way to configure applications at user level (community aspect)
# Verbose feedback
