Description:
Motorsport Youtube channel analytics data pipeline.

How to run the pipeline from a Python terminal:

1. Move to the solution directory:
cd solution

2. Install the required packages found in requirements.txt:
pip install -r requirements.txt

3. Run the code in the terminal:
python main.py

The results should appear as JSON files in the "results" folder.
Two observations:
    - I did not get rid of NaNs as I thought they are relevant entries (e.g. a race can have no results in a real scenario), I just handled them where needed. If mentioned otherwise, I usually follow the exact requirements given.

    - In a real pipeline, I would ask whether the UTC format should be converted to their respective country's timezone based on each race, if needed for showcasing different stats at some point. 

    - I left the notebook I worked in before arranging the code in the main.py as it is my usual way of working, in a separate folder named "extra". It is not presentation-ready by any means.

Stretch goals:
1. The unit tests are written in the "unit_tests_main.py" file, using pytest and can be run as follows:
    1. Make sure you are in the solution directory:
    cd solution
    
    2. In the terminal, execute:
    python -m pytest                           --> (works in bash too)
    (if that gives any erorrs, directly run: pytest unit_test_main.py)

2. Cloud deployment
    - Choose a cloud provider, based on current budget/pricing/licenses (I have worked with Azure and Amazon so far).
    For this hypothetical case, I would choose AWS, as I am the most familiar with.
    - I would store the source-data in separate folders in S3 buckets for efficient loading/unloading, in a platform such as Datalake. I would also take into consideration security measures, such as IAM roles (what I currently do)
    - As a further option, I could execute the script directly in Datalake as well in an appliance and have it scheduled for data transformations as needed, if resources allow it (the dataset does not get too big/heavy to compute).  