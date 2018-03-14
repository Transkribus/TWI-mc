# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class AbbrevTag(models.Model):
    id = models.FloatField(primary_key=True)
    docid = models.ForeignKey('DocMd', models.DO_NOTHING, db_column='docid', blank=True, null=True)
    pageid = models.ForeignKey('Pages', models.DO_NOTHING, db_column='pageid', blank=True, null=True)
    tsid = models.ForeignKey('Transcripts', models.DO_NOTHING, db_column='tsid', blank=True, null=True)
    regionid = models.CharField(max_length=256, blank=True, null=True)
    offset = models.FloatField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    value = models.CharField(max_length=256, blank=True, null=True)
    expansion = models.CharField(max_length=256, blank=True, null=True)
    regiontype = models.CharField(max_length=256, blank=True, null=True)
    context_before = models.CharField(max_length=256, blank=True, null=True)
    context_after = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'abbrev_tag'


class ActionTypes(models.Model):
    type_id = models.FloatField(primary_key=True)
    type = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'action_types'


class Actions(models.Model):
    action_id = models.FloatField(primary_key=True)
    type = models.ForeignKey(ActionTypes, models.DO_NOTHING)
    user_id = models.FloatField()
    user_name = models.CharField(max_length=255)
    time = models.DateTimeField()
    col = models.ForeignKey('Collection', models.DO_NOTHING, blank=True, null=True)
    doc = models.ForeignKey('DocMd', models.DO_NOTHING, blank=True, null=True)
    page = models.ForeignKey('Pages', models.DO_NOTHING, blank=True, null=True)
    client = models.ForeignKey('Clients', models.DO_NOTHING, blank=True, null=True)
    session_history = models.ForeignKey('SessionHistory', models.DO_NOTHING, blank=True, null=True)
    user_role = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'actions'


class Clients(models.Model):
    client_id = models.FloatField(primary_key=True)
    client_name = models.CharField(unique=True, max_length=127)

    class Meta:
        managed = False
        db_table = 'clients'


class Collection(models.Model):
    name = models.CharField(max_length=140)
    description = models.CharField(max_length=4000, blank=True, null=True)
    collection_id = models.FloatField(primary_key=True)
    default_for_app = models.CharField(max_length=20, blank=True, null=True)
    is_crowdsourcing = models.FloatField()
    is_elearning = models.FloatField()
    page = models.ForeignKey('Pages', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'collection'


class CollectionLabels(models.Model):
    label_id = models.FloatField(primary_key=True)
    collection = models.ForeignKey(Collection, models.DO_NOTHING)
    label = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'collection_labels'


class CrowdProject(models.Model):
    proj_id = models.FloatField(primary_key=True)
    aim = models.TextField(blank=True, null=True)
    collection = models.ForeignKey(Collection, models.DO_NOTHING, unique=True)

    class Meta:
        managed = False
        db_table = 'crowd_project'


class CrowdProjectMessage(models.Model):
    id = models.BigIntegerField(primary_key=True)
    milestone = models.ForeignKey('CrowdProjectMilestone', models.DO_NOTHING, blank=True, null=True)
    project = models.ForeignKey(CrowdProject, models.DO_NOTHING, blank=True, null=True)
    subject = models.CharField(max_length=300, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    date_created = models.CharField(max_length=100, blank=True, null=True)
    email_sent = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'crowd_project_message'


class CrowdProjectMilestone(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    project = models.ForeignKey(CrowdProject, models.DO_NOTHING, blank=True, null=True)
    title = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    due_date = models.CharField(max_length=100, blank=True, null=True)
    date_created = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'crowd_project_milestone'


class DateTag(models.Model):
    id = models.FloatField(primary_key=True)
    pageid = models.ForeignKey('Pages', models.DO_NOTHING, db_column='pageid', blank=True, null=True)
    docid = models.ForeignKey('DocMd', models.DO_NOTHING, db_column='docid', blank=True, null=True)
    tsid = models.ForeignKey('Transcripts', models.DO_NOTHING, db_column='tsid', blank=True, null=True)
    regionid = models.CharField(max_length=256, blank=True, null=True)
    offset = models.FloatField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    value = models.CharField(max_length=512, blank=True, null=True)
    year = models.FloatField(blank=True, null=True)
    month = models.FloatField(blank=True, null=True)
    day = models.FloatField(blank=True, null=True)
    calendar = models.CharField(max_length=256, blank=True, null=True)
    notice = models.CharField(max_length=256, blank=True, null=True)
    regiontype = models.CharField(max_length=256, blank=True, null=True)
    context_before = models.CharField(max_length=256, blank=True, null=True)
    context_after = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'date_tag'


class Dict(models.Model):
    dict_id = models.FloatField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=2000, blank=True, null=True)
    language = models.CharField(max_length=60, blank=True, null=True)
    path = models.CharField(max_length=100)
    created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'dict'


class DictCollection(models.Model):
    dict = models.ForeignKey(Dict, models.DO_NOTHING)
    collection = models.ForeignKey(Collection, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'dict_collection'


class DocMd(models.Model):
    docid = models.FloatField(primary_key=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    genre = models.CharField(max_length=63, blank=True, null=True)
    writer = models.CharField(max_length=255, blank=True, null=True)
    scripttype = models.CharField(max_length=63, blank=True, null=True)
    uploader = models.CharField(max_length=320, blank=True, null=True)
    ultimestamp = models.FloatField()
    fimgstorecoll = models.CharField(max_length=63)
    description = models.CharField(max_length=4000, blank=True, null=True)
    extid = models.CharField(max_length=255, blank=True, null=True)
    doctype = models.CharField(max_length=20, blank=True, null=True)
    status = models.FloatField(blank=True, null=True)
    language = models.CharField(max_length=1024, blank=True, null=True)
    createdfrom = models.FloatField(blank=True, null=True)
    createdto = models.CharField(max_length=20, blank=True, null=True)
    uploaderid = models.FloatField(blank=True, null=True)
    origdocid = models.FloatField(blank=True, null=True)
    img = models.ForeignKey('Images', models.DO_NOTHING, blank=True, null=True)
    page = models.ForeignKey('Pages', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'doc_md'


class DocumentCollection(models.Model):
    docid = models.ForeignKey(DocMd, models.DO_NOTHING, db_column='docid', primary_key=True)
    collection = models.ForeignKey(Collection, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'document_collection'
        unique_together = (('docid', 'collection'),)


class EdFeatures(models.Model):
    feature_id = models.FloatField(primary_key=True)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True, null=True)
    collection = models.ForeignKey(Collection, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ed_features'


class EdOptions(models.Model):
    option_id = models.FloatField(primary_key=True)
    feature = models.ForeignKey(EdFeatures, models.DO_NOTHING)
    text = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'ed_options'


class EditDeclaration(models.Model):
    feature = models.ForeignKey(EdFeatures, models.DO_NOTHING, primary_key=True)
    doc = models.ForeignKey(DocMd, models.DO_NOTHING)
    option = models.ForeignKey(EdOptions, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'edit_declaration'
        unique_together = (('feature', 'doc'),)


class Events(models.Model):
    event_id = models.FloatField()
    time = models.DateTimeField()
    message = models.CharField(max_length=4000)
    title = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'events'


class Fimgstore(models.Model):
    storeid = models.FloatField(primary_key=True)
    host = models.CharField(max_length=127)
    context = models.CharField(max_length=63, blank=True, null=True)
    port = models.FloatField(blank=True, null=True)
    username = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fimgstore'


class History(models.Model):
    history_id = models.FloatField(primary_key=True)
    session_history = models.ForeignKey('SessionHistory', models.DO_NOTHING)
    time = models.DateTimeField()
    call = models.CharField(max_length=256)
    parameter = models.CharField(max_length=2048, blank=True, null=True)
    custom = models.CharField(max_length=256, blank=True, null=True)
    collid = models.FloatField(blank=True, null=True)
    docid = models.FloatField(blank=True, null=True)
    pagenr = models.FloatField(blank=True, null=True)
    action_id = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'history'


class Htr(models.Model):
    htr_id = models.FloatField(primary_key=True)
    name = models.CharField(max_length=100)
    provider = models.CharField(max_length=20)
    path = models.CharField(max_length=100)
    created = models.DateTimeField()
    train_gt_docid = models.ForeignKey(DocMd, models.DO_NOTHING, db_column='train_gt_docid', blank=True, null=True)
    description = models.CharField(max_length=2048, blank=True, null=True)
    base_htr = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    train_job = models.ForeignKey('Jobs', models.DO_NOTHING, blank=True, null=True)
    test_gt_docid = models.FloatField(blank=True, null=True)
    language = models.CharField(max_length=50, blank=True, null=True)
    is_preset = models.FloatField(blank=True, null=True)
    params = models.CharField(max_length=2048, blank=True, null=True)
    nr_of_lines = models.FloatField(blank=True, null=True)
    nr_of_words = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'htr'


class HtrCollection(models.Model):
    collection = models.ForeignKey(Collection, models.DO_NOTHING)
    htr = models.ForeignKey(Htr, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'htr_collection'


class HtrModels(models.Model):
    model_id = models.FloatField(primary_key=True)
    model_name = models.CharField(unique=True, max_length=100)
    label = models.CharField(max_length=1024, blank=True, null=True)
    is_usable_in_transkribus = models.FloatField(blank=True, null=True)
    path = models.CharField(unique=True, max_length=1024)
    language = models.CharField(max_length=20, blank=True, null=True)
    nr_of_tokens = models.FloatField(blank=True, null=True)
    nr_of_lines = models.FloatField(blank=True, null=True)
    nr_of_dict_tokens = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'htr_models'


class HtrOutput(models.Model):
    htr_output_id = models.FloatField(primary_key=True)
    pageid = models.ForeignKey('Pages', models.DO_NOTHING, db_column='pageid')
    lineid = models.CharField(max_length=60, blank=True, null=True)
    key = models.CharField(max_length=24)
    htr = models.ForeignKey(Htr, models.DO_NOTHING)
    provider = models.CharField(max_length=60)
    tsid = models.ForeignKey('Transcripts', models.DO_NOTHING, db_column='tsid', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'htr_output'


class Images(models.Model):
    image_id = models.FloatField(primary_key=True)
    imagekey = models.CharField(max_length=24)
    imgfilename = models.CharField(max_length=1024)
    width = models.FloatField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'images'


class JobErrors(models.Model):
    job_err_id = models.FloatField(primary_key=True)
    jobid = models.ForeignKey('Jobs', models.DO_NOTHING, db_column='jobid')
    docid = models.ForeignKey(DocMd, models.DO_NOTHING, db_column='docid')
    pageid = models.ForeignKey('Pages', models.DO_NOTHING, db_column='pageid')
    pagenr = models.FloatField(blank=True, null=True)
    tsid = models.ForeignKey('Transcripts', models.DO_NOTHING, db_column='tsid', blank=True, null=True)
    msg = models.CharField(max_length=2048)
    ex_class = models.CharField(max_length=2048)
    stacktrace = models.TextField()

    class Meta:
        managed = False
        db_table = 'job_errors'


class JobImplRegistry(models.Model):
    job_impl_registry_id = models.FloatField(primary_key=True)
    job_impl = models.CharField(unique=True, max_length=1024)
    job_tasks = models.CharField(max_length=1024)
    job_type = models.CharField(max_length=1024)
    users = models.CharField(max_length=1024, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'job_impl_registry'


class JobModule(models.Model):
    url = models.CharField(primary_key=True, max_length=1024)
    name = models.CharField(max_length=256, blank=True, null=True)
    tasks = models.CharField(max_length=1024, blank=True, null=True)
    version = models.CharField(max_length=256, blank=True, null=True)
    registered_time = models.DateTimeField(blank=True, null=True)
    unregistered_time = models.DateTimeField(blank=True, null=True)
    isactive = models.FloatField(blank=True, null=True)
    service_type = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'job_module'


class Jobs(models.Model):
    jobid = models.FloatField(primary_key=True)
    docid = models.FloatField(blank=True, null=True)
    type = models.CharField(max_length=60)
    state = models.CharField(max_length=31)
    success = models.CharField(max_length=1, blank=True, null=True)
    description = models.CharField(max_length=2048, blank=True, null=True)
    userid = models.CharField(max_length=320, blank=True, null=True)
    starttime = models.FloatField()
    endtime = models.FloatField(blank=True, null=True)
    createtime = models.FloatField(blank=True, null=True)
    pagenr = models.FloatField(blank=True, null=True)
    user_id = models.FloatField(blank=True, null=True)
    jobdata = models.CharField(max_length=4000, blank=True, null=True)
    resumable = models.CharField(max_length=20, blank=True, null=True)
    classname = models.CharField(max_length=100, blank=True, null=True)
    session_history = models.ForeignKey('SessionHistory', models.DO_NOTHING, blank=True, null=True)
    job_impl = models.CharField(max_length=100, blank=True, null=True)
    pages = models.CharField(max_length=50, blank=True, null=True)
    is_scheduled = models.FloatField(blank=True, null=True)
    result = models.CharField(max_length=100, blank=True, null=True)
    jobdata_clob = models.TextField(blank=True, null=True)
    module_url = models.CharField(max_length=256, blank=True, null=True)
    module_name = models.CharField(max_length=256, blank=True, null=True)
    module_version = models.CharField(max_length=256, blank=True, null=True)
    started = models.DateTimeField(blank=True, null=True)
    ended = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    pid = models.CharField(max_length=256, blank=True, null=True)
    batchid = models.FloatField(blank=True, null=True)
    pageid = models.FloatField(blank=True, null=True)
    tsid = models.FloatField(blank=True, null=True)
    regionids = models.CharField(max_length=1024, blank=True, null=True)
    parent_jobid = models.FloatField(blank=True, null=True)
    parent_batchid = models.FloatField(blank=True, null=True)
    stacktrace = models.TextField(blank=True, null=True)
    colid = models.FloatField(blank=True, null=True)
    progress = models.FloatField(blank=True, null=True)
    total_work = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'jobs'


class OtherTag(models.Model):
    id = models.FloatField(primary_key=True)
    docid = models.ForeignKey(DocMd, models.DO_NOTHING, db_column='docid', blank=True, null=True)
    pageid = models.ForeignKey('Pages', models.DO_NOTHING, db_column='pageid', blank=True, null=True)
    tsid = models.ForeignKey('Transcripts', models.DO_NOTHING, db_column='tsid', blank=True, null=True)
    regionid = models.CharField(max_length=256, blank=True, null=True)
    offset = models.FloatField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    value = models.CharField(max_length=256, blank=True, null=True)
    tagname = models.CharField(max_length=256, blank=True, null=True)
    attributes = models.CharField(max_length=2048, blank=True, null=True)
    regiontype = models.CharField(max_length=256, blank=True, null=True)
    context_before = models.CharField(max_length=256, blank=True, null=True)
    context_after = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'other_tag'


class PageImageVersions(models.Model):
    page_image_versions_id = models.FloatField(primary_key=True)
    pageid = models.ForeignKey('Pages', models.DO_NOTHING, db_column='pageid')
    type = models.CharField(max_length=255)
    description = models.CharField(max_length=2048, blank=True, null=True)
    translation_x = models.FloatField(blank=True, null=True)
    translation_y = models.FloatField(blank=True, null=True)
    scaling_x = models.FloatField(blank=True, null=True)
    scaling_y = models.FloatField(blank=True, null=True)
    rotation = models.FloatField(blank=True, null=True)
    imagekey = models.CharField(max_length=24)
    tsid = models.ForeignKey('Transcripts', models.DO_NOTHING, db_column='tsid', blank=True, null=True)
    created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'page_image_versions'
        unique_together = (('pageid', 'type', 'tsid'),)


class Pages(models.Model):
    docid = models.ForeignKey(DocMd, models.DO_NOTHING, db_column='docid')
    pagenr = models.FloatField()
    imagekey = models.CharField(max_length=24, blank=True, null=True)
    imgfilename = models.CharField(max_length=1024, blank=True, null=True)
    pageid = models.FloatField(primary_key=True)
    image = models.ForeignKey(Images, models.DO_NOTHING)
    is_indexed = models.FloatField()
    tags_stored = models.DateTimeField(blank=True, null=True)
    img_problem = models.CharField(max_length=2048, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pages'


class Permissions(models.Model):
    docid = models.ForeignKey(DocMd, models.DO_NOTHING, db_column='docid', primary_key=True)
    username = models.CharField(max_length=320, blank=True, null=True)
    role = models.CharField(max_length=20)
    userid = models.FloatField()

    class Meta:
        managed = False
        db_table = 'permissions'
        unique_together = (('docid', 'userid'),)


class PersonTag(models.Model):
    id = models.FloatField(primary_key=True)
    docid = models.ForeignKey(DocMd, models.DO_NOTHING, db_column='docid', blank=True, null=True)
    pageid = models.ForeignKey(Pages, models.DO_NOTHING, db_column='pageid', blank=True, null=True)
    tsid = models.ForeignKey('Transcripts', models.DO_NOTHING, db_column='tsid', blank=True, null=True)
    regionid = models.CharField(max_length=256, blank=True, null=True)
    offset = models.CharField(max_length=256, blank=True, null=True)
    length = models.CharField(max_length=256, blank=True, null=True)
    value = models.CharField(max_length=256, blank=True, null=True)
    firstname = models.CharField(max_length=512, blank=True, null=True)
    lastname = models.CharField(max_length=512, blank=True, null=True)
    middlename = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.CharField(max_length=512, blank=True, null=True)
    death_date = models.CharField(max_length=512, blank=True, null=True)
    occupation = models.CharField(max_length=256, blank=True, null=True)
    notice = models.CharField(max_length=256, blank=True, null=True)
    place_of_birth = models.CharField(max_length=256, blank=True, null=True)
    place_of_death = models.CharField(max_length=256, blank=True, null=True)
    regiontype = models.CharField(max_length=256, blank=True, null=True)
    context_before = models.CharField(max_length=256, blank=True, null=True)
    context_after = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'person_tag'


class PlaceTag(models.Model):
    id = models.FloatField(primary_key=True)
    docid = models.ForeignKey(DocMd, models.DO_NOTHING, db_column='docid', blank=True, null=True)
    pageid = models.ForeignKey(Pages, models.DO_NOTHING, db_column='pageid', blank=True, null=True)
    tsid = models.ForeignKey('Transcripts', models.DO_NOTHING, db_column='tsid', blank=True, null=True)
    regionid = models.CharField(max_length=256, blank=True, null=True)
    offset = models.FloatField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    value = models.CharField(max_length=512, blank=True, null=True)
    country = models.CharField(max_length=256, blank=True, null=True)
    regiontype = models.CharField(max_length=256, blank=True, null=True)
    context_before = models.CharField(max_length=256, blank=True, null=True)
    context_after = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'place_tag'


class SessionHistory(models.Model):
    session_id = models.CharField(max_length=128)
    created = models.DateTimeField()
    last_refresh = models.DateTimeField(blank=True, null=True)
    user_id = models.BigIntegerField(blank=True, null=True)
    useragent = models.CharField(max_length=512, blank=True, null=True)
    ip = models.CharField(max_length=50, blank=True, null=True)
    destroyed = models.DateTimeField(blank=True, null=True)
    session_history_id = models.FloatField(primary_key=True)
    gui_version = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'session_history'
        unique_together = (('session_id', 'created'),)


class TagDefs(models.Model):
    id = models.FloatField(primary_key=True)
    def_field = models.CharField(db_column='def', max_length=2048, blank=True, null=True)  # Field renamed because it was a Python reserved word.
    color = models.CharField(max_length=20, blank=True, null=True)
    col_id = models.FloatField(blank=True, null=True)
    description = models.CharField(max_length=2048, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tag_defs'


class TagDefsCollection(models.Model):
    collid = models.ForeignKey(Collection, models.DO_NOTHING, db_column='collid', primary_key=True)
    tagdefs = models.BinaryField()

    class Meta:
        managed = False
        db_table = 'tag_defs_collection'


class Transcripts(models.Model):
    xmlkey = models.CharField(max_length=24)
    docid = models.FloatField(blank=True, null=True)
    pagenr = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=24)
    userid = models.CharField(max_length=320)
    timestamp = models.FloatField()
    user_id = models.FloatField(blank=True, null=True)
    toolname = models.CharField(max_length=2048, blank=True, null=True)
    pageid = models.ForeignKey(Pages, models.DO_NOTHING, db_column='pageid')
    tsid = models.FloatField(primary_key=True)
    parent_tsid = models.FloatField(blank=True, null=True)
    note = models.CharField(max_length=1023, blank=True, null=True)
    nr_of_regions = models.FloatField(blank=True, null=True)
    nr_of_transcribed_regions = models.FloatField(blank=True, null=True)
    nr_of_words_in_regions = models.FloatField(blank=True, null=True)
    nr_of_lines = models.FloatField(blank=True, null=True)
    nr_of_transcribed_lines = models.FloatField(blank=True, null=True)
    nr_of_words_in_lines = models.FloatField(blank=True, null=True)
    nr_of_words = models.FloatField(blank=True, null=True)
    nr_of_transcribed_words = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transcripts'


class Uploads(models.Model):
    upload_id = models.FloatField(primary_key=True)
    created = models.DateTimeField()
    finished = models.DateTimeField(blank=True, null=True)
    user_id = models.FloatField(blank=True, null=True)
    username = models.CharField(max_length=1024, blank=True, null=True)
    nr_of_pages = models.FloatField(blank=True, null=True)
    type = models.CharField(max_length=20)
    job_id = models.FloatField(blank=True, null=True)
    collection = models.ForeignKey(Collection, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'uploads'


class UserCollection(models.Model):
    user_id = models.FloatField(primary_key=True)
    collection = models.ForeignKey(Collection, models.DO_NOTHING)
    is_default = models.FloatField()
    role = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'user_collection'
        unique_together = (('user_id', 'collection'),)


class Wordgraphs(models.Model):
    docid = models.FloatField(blank=True, null=True)
    wordgraphkey = models.CharField(max_length=24)
    text = models.CharField(max_length=255, blank=True, null=True)
    lineid = models.CharField(primary_key=True, max_length=100)
    pagenr = models.FloatField(blank=True, null=True)
    nbestkey = models.CharField(max_length=24, blank=True, null=True)
    model = models.ForeignKey(HtrModels, models.DO_NOTHING, blank=True, null=True)
    pageid = models.ForeignKey(Pages, models.DO_NOTHING, db_column='pageid')

    class Meta:
        managed = False
        db_table = 'wordgraphs'
        unique_together = (('lineid', 'pageid'),)
