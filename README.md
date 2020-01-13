## MERIT System for rehoming service chains of VNFs deployed with Openstack
The system is designed to work with any platform that supports rehoming actions, we currently include an orchestration layer for Openstack but it can easily be replaced with another one for a different platform like Kubernetes or Docker as long as an appropriate wrapper class is provided (see ROrc.py - all methods should be available in new wrapper).

**To start the system execute:**

python rehome.py [CONF_FILE] [MODEL_DIR]
e.g. `python rehome.py test.txt .`

where `CONF_FILE` is the file containing VNF information, see test.txt as an example.
and `MODEL_DIR` is the directory where sklearn models are present.

Predictive models are included as *.pkl* files, and are readable through both python2 and python3. We currently use python2 for backward compatibility. 
