import json
import os

import behave


@behave.given(u'I have an app entity from "{path}"')
def step_impl(context, path):
    json_path = os.path.join(os.environ['DATALOOP_TEST_ASSETS'], path)
    with open(json_path) as f:
        data = json.load(f)
    context.dpk = context.dl.entities.Dpk.from_json(_json=data, client_api=context.project._client_api)


@behave.given(u'publish the app')
def step_impl(context):
    context.dpk = context.dl.dpks.publish(dpk=context.dpk, project=context.project)


@behave.when(u'I install the app with exception')
def step_impl(context):
    try:
        context.app = context.project.apps.install(context.app)
    except Exception as e:
        context.e = e


@behave.when(u'I install the app')
@behave.given(u'I install the app')
def step_impl(context):
    context.app = context.dl.entities.App.from_json({

    }, client_api=context.project._client_api, project=context.project)
    context.app = context.project.apps.install(context.dpk)


@behave.then(u'I should get the app with the same id')
def step_impl(context):
    assert context.app.id == context.project.apps.get(app_id=context.app.id).id


@behave.then(u"I should get an exception error='{error_code}'")
def step_impl(context, error_code):
    assert context.e is not None and context.e.status_code == error_code
