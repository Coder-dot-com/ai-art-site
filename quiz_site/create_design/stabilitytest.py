import io
import os
import warnings

from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation


stability_api = client.StabilityInference(
    key="", 
    verbose=True,
)


answers = stability_api.generate(
    prompt="portrait",
    init_image=Image.open("/home/user/Desktop/dev/ai-art-site/frontend templates/webadmin-responsive-admin-dashboard-template-2022-04-27-05-06-32-utc/WebAdmin_v2.0.0/Admin/dist/assets/images/calendar-img.png"),
    start_schedule=0.6, # this controls the "strength" of the prompt relative to the init image
)

# iterating over the generator produces the api response
for resp in answers:
    for artifact in resp.artifacts:
        if artifact.finish_reason == generation.FILTER:
            warnings.warn(
                "Your request activated the API's safety filters and could not be processed."
                "Please modify the prompt and try again.")
        if artifact.type == generation.ARTIFACT_IMAGE:
            img2 = Image.open(io.BytesIO(artifact.binary))
            img2.save("/home/user/Desktop/dev/ai-art-site/quiz_site/create_design/stabilitytest.jpg")

