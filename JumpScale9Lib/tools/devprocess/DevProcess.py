from JumpScale import j
import sys
import re
import collections
from jinja2 import Template
import threading
import itertools
from json import loads, dumps
import telegram  # python-telegram-bot
from datetime import datetime
import github

pickle_dump = dumps
pickle_load = loads

NOMILESTONE = '__no_milestone__'

MILESTONE_REPORT_FILE = 'milestone-report.md'
ASSIGNEE_REPORT_FILE = 'assignee-report.md'

# MILESTONE REPORT
MILESTONE_REPORT_TMP = Template('''\
> This file is auto generated by `ays` services. Please don't modify manually.

# Summary
|Milestone|ETA|
|---------|---|
{% for milestone in milestones.values() -%}
|[{{ milestone.title }}](#milestone-{{ milestone.title | replace(' ', '-')| replace('.', '')| lower }})|{{ summary(milestone.title) }}|
{% endfor -%}
|[No milestone](#no-milestone)|{{ summary('__no_milestone__') }}|

{% for key, milestone in milestones.items() -%}
## [Milestone {{ milestone.title }}](milestones/{{ key }}.md)

{% set issues = report.get(milestone.title, []) %}
|Issue|Title|State|Owner|ETA|
|-----|-----|-----|-----|---|
{% for issue in issues -%}
|[#{{ issue.number }}](https://github.com/{{ repo.fullname }}/issues/{{ issue.number }})|\
{{ issue.title }}|\
{{ state(issue.state) }}|\
{% if issue.assignee %}[{{ issue.assignee }}](https://github.com/{{ issue.assignee }}){% endif %}|\
{% set eta, id = estimate(issue) %}{% if eta %}[{{ eta|trim }}]({{ issue.url }}#issuecomment-{{ id }}){% else %}N/A{% endif %}|
{% endfor %}
{% endfor %}


## No milestone
|Issue|Tiklkle|State|Owner|ETA|
|-----|-----|-----|-----|---|
{% for issue in report.get('__no_milestone__', []) -%}
|[#{{ issue.number }}](https://github.com/{{ repo.fullname }}/issues/{{ issue.number }})|\
{{ issue.title }}|\
{{ state(issue.state) }}|\
{% if issue.assignee %}[{{ issue.assignee }}](https://github.com/{{ issue.assignee }}){% endif %}|\
{% set eta, id = estimate(issue) %}{% if eta %}[{{ eta|trim }}]({{ issue.url }}#issuecomment-{{ id }}){% else %}N/A{% endif %}|
{% endfor %}
''')


# MILESTONE DETAILS TEMPLATE
MILESTONE_DETAILS_TEMP = Template('''\
> This file is auto generated by `ays` services. Please don't modify manually.

# Milestone {{milestone.title}}

## List of all unassigned issues in this milestone

|Issue|Title|State|Type|
|-----|-----|-----|---|
{% for issue in issues -%}
{% if issue.milestone == key and not issue.assignee and issue.isOpen -%}
|[#{{ issue.number }}](https://github.com/{{ repo.fullname }}/issues/{{ issue.number }})|\
{{ issue.title }}|\
{{ state(issue.state) }}|\
{{ issue.type }}|
{% endif -%}
{% endfor %}

## Issues per assignee
{% for user, issues in assignees.items() -%}
- [{{ user }}](#{{ user|replace(' ', '-')|replace('.', '')|lower }})
{% endfor %}

{% for user, issues in assignees.items() %}
### [{{ user }}](https://github.com/{{user}})

|Issue|Title|State|Type|
|-----|-----|-----|----|
{% for issue in issues -%}
{% if issue.milestone == key -%}
|[#{{ issue.number }}](https://github.com/{{ repo.fullname }}/issues/{{ issue.number }})|\
{{ issue.title }}|\
{{ state(issue.state) }}|\
{{ issue.type }}|
{% endif -%}
{% endfor %}
{% endfor %}
    ''')

# ASSIGNEE REPORT TEMPLATE
ASSIGNEE_REPORT_TMP = Template('''\
> This file is auto generated by `ays` services. Please don't modify manually.

# Issues per assignee
{% for user, issues in assignees.items() -%}
- [{{ user }}](#{{ user|replace(' ', '-')|replace('.', '')|lower }}) has {{ issues|count }} assigned
{% endfor %}

{% for user, issues in assignees.items() %}
## [{{ user }}](https://github.com/{{user}})

|Issue|Title|State|Type|
|-----|-----|-----|----|
{% for issue in issues -%}
|[#{{ issue.number }}](https://github.com/{{ repo.fullname }}/issues/{{ issue.number }})|\
{{ issue.title }}|\
{{ state(issue.state) }}|\
{{ issue.type }}|
{% endfor %}
{% endfor %}
''')

re_story_name = re.compile('.+\((.+)\)\s*$')   # EXTRACT STORY NAME
re_task_estimate = re.compile('.+\[([^\]]+)\]\s*$')  # TASK ESTIMATES
re_story_estimate = re.compile('^ETA:\s*(.+)\s*$', re.MULTILINE)  # STORY ESTIMATES


class DevProcess:

    def __init__(self):
        self.__jslocation__ = "j.tools.devprocess"
        self.logger = j.logger.get("j.tools.devprocess")
        self.lock = threading.RLock()

    def raise_event(self, event_name, args=[]):
        """
        push event to ays daemon.

        @param event_name string: event name.
        @param args list: event arguments
        """

        redis_config = j.atyourservice.config['redis']
        command_queue = j.servers.kvs.getRedisStore("ays_server", namespace='db', **redis_config)
        payload = {"command": "event", "event": event_name, "args": args}
        self.logger.info("payload: ", payload)
        command_queue.queuePut("command", j.data.serializer.json.dumps(payload))

    def notify(self, handle, message):
        """
        Send notifications on telegram.

        @param handle string: telegram handle.
        @param message string: message to be sent.
        """

        self.logger.info("Calling notify: {handle} {message}".format(**locals()))


    def _notify(self, service, message):
        # if service.model.data.repoType != "org":
        #     return

        acc = service.producers['github_account'][0]
        botkey = acc.model.data.telegramToken
        telegramhandle = acc.model.data.telegramHandle
        self.logger.info("Notifying {service} with: {message}".format(**locals()))
        if botkey and telegramhandle:
            bot = telegram.Bot(botkey)
            bot.send_message(telegramhandle, message)

    def set_labels(self, service):
        """
        set labels on a repository

        @param service github_repo: service object.

        """
        # service: repo service.
        config = service.producers['github_config'][0]
        yml = config.model.data.hrd
        labelsfromyaml = j.data.serializer.yaml.loads(yml)
        projtype = service.model.data.repoType
        labels = []
        for k, g in itertools.groupby(sorted(labelsfromyaml), lambda k: k if k.startswith('github.label') else None):
            if k:
                vals = labelsfromyaml[k]
                label = k.replace("github.label.", "").replace(".", "_")
                if projtype in vals or "*" in vals:
                    labels.append(label)

        r = self.get_github_repo(service)
        #  first make sure issues get right labels
        try:
            r.labelsSet(labels, ignoreDelete=["p_"])
        except:
            # labels already exists (just ignore it for now)
            pass

    def sync_milestones(self, service):
        """
        Sync milestones of a repo.
        service: github_repo service

        """
        repo = self.get_github_repo(service=service) # GithubRepo
        actor = service.aysrepo.actorGet('github_milestone')
        repomilestones = []
        for milestone in repo.milestones:
            repomilestones.append(milestone.title)
            args = {
                # github.repo': service.name,
                'milestone.title': milestone.title,
                'milestone.description': milestone.description,
                'milestone.deadline': milestone.deadline,
                'pickledmodel': pickle_dump(milestone.ddict),
            }
            mservice = actor.serviceCreate(instance=str(milestone.title), args=args)
            service.consume(mservice)
            service.saveAll()
        allmilestones = service.producers.get('github_milestone', [])
        tocreate = []
        if allmilestones:
            tocreate = set(x.name for x in allmilestones) - set(repomilestones)

        for m in tocreate:
            msv = service.aysrepo.serviceGet("github_milestone", m)
            dueon = github.GithubObject.NotSet
            if msv.model.data.milestoneDeadline:
                dueon = datetime.strptime(msv.model.data.milestoneDeadline, "%Y-%m-%d") ##FIXME NOTWORKING
                dueon = dueon.strftime("%Y-%m-%dT%H:%M:%SZ")
                dueon = datetime.strptime(dueon, "%Y-%m-%dT%H:%M:%SZ")
            kwargs = {
                'title': msv.model.data.milestoneTitle if msv.model.data.milestoneTitle else msv.name,
                'description': msv.model.data.milestoneDescription,
            }
            try:
                milestone = repo.api.create_milestone(**kwargs) # repo.createMilestone doesn't work.
                milestone.edit(kwargs['title'], due_on=dueon) ## error in PyGithub
            except Exception as e: ## github.GithubException.GithubException, 422
                self.logger.error(e)

    def getGithubClient(self, service):
        """
        Get a github client from github_repo service.

        @param service Service: github_repo service object
        """

        g = j.clients.github.getClient(service.model.data.githubSecret)
        return g

    def get_issues_from_ays(self, service):
        """
        Get issues from a github_repo service.

        @param service Service: github_repo service object.

        """
        repo = self.get_github_repo(service)
        issues = []
        Issue = j.clients.github.getIssueClass()

        for child in service.children:
            if child.model.role != 'github_issue':
                continue
            issuemodel = pickle_load(child.model.data.pickledmodel)
            issue = Issue(repo=repo, ddict=issuemodel)
            issues.append(issue)

        return issues

    def get_github_repo(self, service, repokey=None):
        """
        Get github api repo object from github_repo service.
        @param service Service: github_repo service.

        """
        githubclientays = service.producers['github_client'][0]
        client = self.getGithubClient(service=githubclientays)
        if not repokey:
            repokey = service.model.data.repoAccount + "/" + service.model.data.repoName
        return client.getRepo(repokey)

    def _check_deadline(self, service, milestones, report):
        """
        Checks if stories are falling behind deadline.

        @param service Service: github_repo service (should be org)
        @param milestones List[Milestone]: milestones api list.
        @param report dict: dict of milestone to stories.
        """

        stories_behind_deadline = set()

        for milestone_key, stories in report.items():
            if milestone_key == NOMILESTONE:
                continue
            milestone = None
            deadline = None
            for story in stories:
                if milestone is None:
                    #note that milestones keys are in 'number:title' so we can only retrieve it via the issue reference.
                    milestone = milestones[story.milestone]
                    deadline = j.data.time.any2epoch(milestone.deadline)

                dl, _ = self._story_deadline(story)
                if dl > deadline:
                    stories_behind_deadline.add(self._issue_url(story))

        # BATCH SEND behind deadline notification
        if stories_behind_deadline:
            behind_deadline_msg = 'Stories behind milestone deadline: \n' + "\n".join(stories_behind_deadline)
            self._notify(service, behind_deadline_msg)

    def _process_issues(self, service, repo, issues=None):
        """
        Process issues will find all the issues in the repo and label them according to the
        detected type (story, or task) add the proper linking of tasks to their parent stories, and
        adds a nice table in the story to list all story tasks.

        The tool, will also generate and commit some reports (in markdown syntax) with milestones, open stories
        assignees and estimates.

        It will also process the todo's comments

        !! prio $prio  ($prio is checked on first 4 letters, e.g. critical, or crit matches same)
        !! p $prio (alias above)

        !! move gig-projects/home (move issue to this project, try to keep milestones, labels, ...)
        """
        if issues is None:
            issues = repo.issues

        org_repo = self._is_org_repo(repo.name)
        # Do not complete if repo is not supported
        if not org_repo:
            return
        with self.lock:
            # repos = all repos that consumes this specific org repo.
            repos = service.consumers.get('github_repo', [])
            for repo_service in repos:
                rep = self.get_github_repo(repo_service)  #  DON'T MESS UP THE REPO local variable
                issues.extend(rep.issues)

            issues = sorted(issues, key=lambda i: i.number)

            stories = self._process_stories(service, issues)

            _ms = [('{m.number}:{m.title}'.format(m=m), m) for m in repo.milestones]
            milestones = collections.OrderedDict(sorted(_ms, key=lambda i: i[1].title))
            report = dict()
            self._process_todos(repo, issues)

            no_estimate_tasks = set()
            stories_tasks = dict()
            for issue in issues:
                if self._is_story(issue) and issue.isOpen:
                    key = NOMILESTONE
                    if issue.milestone:
                        ms = milestones.get(issue.milestone, None)
                        if ms is not None:
                            key = ms.title

                    report.setdefault(key, [])
                    report[key].append(issue)

                start = issue.title.partition(":")[0].strip()
                if start not in stories:
                    # FIXME: what if a task doesn't belong to a story?.
                    continue

                story = stories[start]
                labels = issue.labels
                labels_dirty = False

                if "type_task" not in labels:
                    labels.append("type_task")
                    labels_dirty = True

                if self._task_estimate(issue.title) is None:
                    no_estimate_tasks.add(self._issue_url(issue))
                    if "task_no_estimation" not in labels:
                        labels.append("task_no_estimation")
                        labels_dirty = True
                else:
                    # pop label out
                    if "task_no_estimation" in labels:
                        labels.remove("task_no_estimation")
                        labels_dirty = True

                if labels_dirty:
                    # Only update labels if it was changed.
                    self.logger.debug('setting issue label')
                    issue.labels = labels

                # create link between story and tasks
                # linking logic
                self._task_link_to_story(story, issue)
                tasks = stories_tasks.setdefault(story, [])
                tasks.append(issue)

            # update story links
            for story, tasks in stories_tasks.items():
                self._story_add_tasks(story, tasks)

            self._check_deadline(service, milestones, report)
            self._generate_views(repo, milestones, issues, report)

            # tasks with no estimates notification.
            if no_estimate_tasks:
                no_estimate_notification = "Tasks with no estimation:\n" + '\n'.join(no_estimate_tasks)
                self._notify(service, no_estimate_notification)


    def _process_stories(self, service, issues):
        """
        Process stories
        """

        if service.model.data.repoType != 'org':
            return
        # make sure all stories are auto labeled correctly
        stories = dict()
        stories_with_no_owner = set()
        for issue in issues:
            if issue.repo.type not in ['home', 'proj', 'milestone', 'org', 'code']:
                continue

            story_name = self._story_name(issue.title)
            if story_name is not None:
                if not issue.assignee:
                    stories_with_no_owner.add("Story %s has no owner" % self._issue_url(issue))
                stories[story_name] = issue
                if issue.type != 'story':
                    issue.type = 'story'

        errstring = "Stories with no owner:"
        errstring += '\n'.join(stories_with_no_owner)
        self._notify(service, errstring)
        return stories

    def process_issues(self, service, refresh=False):
        """
        refresh: bool, force loading of issue from github
        """

        self.sync_milestones(service=service)

        repo = self.get_github_repo(service=service)
        if refresh:
            # force reload of services from github.
            repo._issues = None
        else:
            # load issues from ays.
            repo._issues = self.get_issues_from_ays(service=service)
        githubissue_actor = service.aysrepo.actorGet('github_issue')
        for issue in repo.issues:
            args = {
                'github.repo': service.name,
                'pickledmodel': pickle_dump(issue.ddict)
            }

            githubissue_actor.serviceCreate(instance=str(issue.id), args=args)
        self._process_issues(service, repo)

    def _is_org_repo(self, name):
        """Check if repo name starts with our supported initials."""
        SUPPORTED_REPOS = ('org_', 'proj_')
        for typ in SUPPORTED_REPOS:
            if name.lower().startswith(typ):
                return True
        return False

    def _story_deadline(self, issue):
        """
        return the deadline of certain issue

        @param issue Issue: issue object.
        """
        eta, id = self._story_estimate(issue)
        try:
            return j.data.time.getEpochFuture(eta), id
        except:
            pass
        try:
            return j.data.time.any2epoch(eta), id
        except:
            pass

        return 0, id

    def _generate_views(self, repo, milestones, issues, report):
        """
        Generates views

        @param repo :
        @param milestones :
        @param issues :
        @param report :

        """

        def summary(ms):
            issues = report.get(ms, [])
            ts = 0
            for issue in issues:
                eta_stamp, _ = self._story_deadline(issue)
                if eta_stamp > ts:
                    ts = eta_stamp

            if ts:
                return j.data.time.epoch2HRDate(ts)
            else:
                return 'N/A'

        def state(s):
            if s == 'verification':
                return ':white_circle: Verification'
            elif s == 'inprogress':
                return ':large_blue_circle: In Progress'
            else:
                return ':red_circle: Open'

        def estimate(issue):
            eta, id = self._story_deadline(issue)
            if eta:
                return j.data.time.epoch2HRDate(eta), id
            return None, None

        view = MILESTONE_REPORT_TMP.render(repo=repo, report=report, milestones=milestones,
                                           summary=summary, state=state, estimate=estimate)

        repo.set_file(MILESTONE_REPORT_FILE, view)

        # group per user
        assignees = dict()
        for issue in issues:
            if not issue.assignee or not issue.isOpen:
                continue

            assignees.setdefault(issue.assignee, [])
            assignees[issue.assignee].append(issue)

        # sort the assignees dict.
        assignees = collections.OrderedDict(sorted([(k, v) for k, v in assignees.items()], key=lambda i: i[0]))

        # generate milestone details page
        for key, milestone in milestones.items():
            view = MILESTONE_DETAILS_TEMP.render(repo=repo, key=key, milestone=milestone,
                                                 issues=issues, assignees=assignees, state=state)
            repo.set_file("milestones/%s.md" % key, view)

        # assignee details page
        view = ASSIGNEE_REPORT_TMP.render(repo=repo, assignees=assignees, state=state)
        repo.set_file(ASSIGNEE_REPORT_FILE, view)

    def pull(self, service):
        """
        Pull git repository of certain service.

        @param service Service: github_repo service object.
        """
        j.do.pullGitRepo(url=service.model.data.repoUrl,
                         dest=service.model.data.codePath,
                         login=None, passwd=None, depth=1,
                         ignorelocalchanges=False, reset=False, branch=None,
                         revision=None, ssh=True, executor=None, codeDir=None)

    # HELPERS
    def getGithubClientFromSecret(self, secret):
        """
        Get github client using token.

        @param secret string: github secret token.
        """
        g = j.clients.github.getClient(secret)
        return g

    def _task_estimate(self, title):
        """
        Calcuate task estimate from the issue title based on ETA within square brackets for example [2h] or [5d]


        @param title string: task title
        """
        m = re_task_estimate.match(title)
        if m is not None:
            return m.group(1).strip()
        return None

    def _story_estimate(self, issue):
        """
        Calculate the story time estimate.

        @param issue Issue: Issue object
        """
        comments = issue.comments
        if not len(comments):
            return None, None
        # find last comment with ETA
        for last in reversed(comments):
            m = re_story_estimate.search(last['body'])
            if m is not None:
                return m.group(1), last['id']
        return None, None

    def _issue_url(self, issue):
        """
        returns issue URL on github based on the issue object

        (i.e: https://github.com/{username}/issues/{issue_id})

        @param issue Issue: issue to render its URL.
        """
        return 'https://github.com/{fullname}/issues/{issuenumber}'.format(fullname=issue.repo.fullname, issuenumber=issue.number)

    def _move_to_repo(self, issue, dest):
        """
        Moves issue to a certain destination repo

        @param issue Issue: issue object.
        @param dest Repository: destination repository object.
        """
        self.logger.info("%s: move to repo:%s" % (issue, dest))
        ref = self._issue_url(issue)
        body = "Issue moved from %s\n\n" % ref

        for line in issue.api.body.splitlines():
            if line.startswith("!!") or line.startswith(
                    '### Tasks:') or line.startswith('### Part of Story'):
                continue
            body += "%s\n" % line

        assignee = issue.api.assignee if issue.api.assignee else NotSet
        labels = issue.api.labels if issue.api.labels else NotSet
        moved_issue = dest.api.create_issue(title=issue.title, body=body,
                                            assignee=assignee, labels=labels)
        moved_issue.create_comment(self._create_comments_backlog(issue))
        moved_ref = 'https://github.com/%s/issues/%s' % (dest.fullname, moved_issue.number)
        issue.api.create_comment("Moved to %s" % moved_ref)
        issue.api.edit(state='close')  # we shouldn't process todos from closed issues.

    def _create_comments_backlog(self, issue):
        out = "### backlog comments of '%s' (%s)\n\n" % (issue.title, issue.url)

        for comment in issue.api.get_comments():
            if comment.body.find("!! move") != -1:
                continue
            date = j.data.time.any2HRDateTime(
                [comment.last_modified, comment.created_at])
            out += "from @%s at %s\n" % (comment.user.login, date)
            out += comment.body + "\n\n"
            out += "---\n\n"
        return out

    def _is_story(self, issue):
        """
        Checks if a certain issue is a story based on the type or if it contains a story name.

        @param issue Issue: issue object.
        """
        return issue.type == 'story' or self._story_name(issue.title) is not None

    def kanban_link(self, storycard_name):
        """
        Create kanban link for certain story card.

        @param storycard_name string: Get kanban link.
        """
        return "# Waffle: [kanban](https://waffle.io/gig-projects/org_development?search={storycard_name}:&label=type_task)".format(**locals())

    def _story_add_tasks(self, story, tasks):

        """
        If this issue is a story, add a link to a subtasks

        @param story Issue: story object.
        @param tasks List[Issue]: list of issue objects.
        """

        if not self._is_story(story):
            j.exceptions.Input("This issue is not a story")
            return

        def state(s):
            """
            used for the issue checkbox [x] or []
            """
            s = s.lower()
            if s == 'closed':
                return 'x'
            else:
                return ' '

        doc = j.data.markdown.getDocument(story.body)

        items = []  # here we save the non generated items
        intasksblock = False

        for idx, item in enumerate(doc.items):
            if item.type == "block":
                if item.text.startswith("![Progress]"):
                    continue
                else:
                    items.append(item)
            if item.type == "header":
                intasksblock = False
                if item.title.startswith("Tasks"):
                    intasksblock = True
                elif item.title.startswith("Remaining"):
                    continue
                elif item.title.startswith("Waffle"):
                    continue
            if item.type == "list" and intasksblock:
                continue

        newdoc = j.data.markdown.getDocument()
        newdoc.items = items
        # CREATE TASKS BLOCK
        newdoc.addMDBlock("# Tasks")
        for task in tasks:
            # ADD EACH ISSUE AS A LIST ITEM RIGHT AFTER THE TASKS BLOCK
            line = '- [{state}] {task_title} #[{task_num}]({task_url}) '.format(state=state(task.api.state), task_title=task.title,
                                                                                task_num=task.number,task_url=self._issue_url(task))
            newdoc.addMDListItem(0, line)

        progress, remaining_time = self.calculate_story_progress(story, tasks)
        # CREATE REMAINING TIME BLOCK
        newdoc.addMDBlock("# Remaining Time: %sh" % remaining_time)
        newdoc.addMDBlock("![Progress](http://progressed.io/bar/%s)" % progress)
        newdoc.addMDBlock(self.kanban_link(storycard_name=self._story_name(story.title)))

        body = str(newdoc)

        if body != story.body:
            story.api.edit(body=body)

    def calculate_story_progress(self, story, tasks):
        """
        Calculate the progress of tasks in certain story.

        @param story Issue: story object.
        @param tasks List[Issue]: list of issues.
        """
        total_estimation = 0
        remaining_time = 0
        progress = 0
        done = 0

        for task in tasks:
            estimation = self._task_estimate(task.title)
            if estimation:
                m = re.match(r'(\d+)(\w)', estimation)
                if not m:
                    continue
                estimation_time = m.group(1)
                estimation_unit = m.group(2)
                if estimation_unit == 'd':
                    estimation_time = float(estimation_time) * 8
                total_estimation += int(estimation_time)
                if task.api.state == 'closed':
                    done += int(estimation_time)

                else:
                    remaining_time += int(estimation_time)
        if total_estimation:
            progress = (done*100) / total_estimation
        return (int(progress), remaining_time)

    def _story_name(self, title):
        """
        Extract story name from story title.

        @param title string: story title.
        """
        m = re_story_name.match(title.strip())
        if m is None:
            return None

        return m.group(1)

    def _task_link_to_story(self, story, task):
        """
        If this issue is a task from a story, add link in to the story in the description

        @param story Issue: story object.
        @param task Issue: task object.

        """

        body = task.body
        if body is None:
            body = ''

        doc = j.data.markdown.getDocument(body)

        change = False
        header = None
        for item in doc.items:
            if item.type == 'header' and item.level == 3 and item.title.find("Part of Story") != -1:
                header = item
                break

        if header is not None:
            title = 'Part of Story: #[{issue_number}]({issue_url})'.format(issue_number=story.number,
                                                                           issue_url=self._issue_url(story))
            if title != header.title:
                header.title = title
                change = True
        else:
            change = True
            doc.addMDHeader(3, 'Part of Story: #[{issue_number}]({issue_url})'.format(issue_number=story.number,
                                                                                      issue_url=self._issue_url(story)))
            # make sure it's on the first line of the comment
            title = doc.items.pop(-1)
            doc.items.insert(0, title)

        if change:
            self.logger.info("%s: link to story:%s" % (task, story))
            task.body = str(doc)

    def _process_todos(self, repo, issues):
        priorities_map = {
            'crit': 'critical',
            'mino': 'minor',
            'norm': 'normal',
            'urge': 'urgent',
        }

        client = repo.client

        for issue in issues:
            # only process open issues.
            if not issue.isOpen:
                continue

            for todo in issue.todo:
                cmd, _, args = todo.partition(' ')

                if not args:
                    # it seems all commands requires arguments
                    self.logger.warning("cannot process todo for %s" % (todo,))
                    continue

                if cmd == 'move':
                    destination_repo = client.getRepo(args)
                    self._move_to_repo(issue, destination_repo)
                    story_name = self._story_name(issue.title)
                    if story_name is not None:
                        for task in self._story_tasks(story_name, issues):
                            self._move_to_repo(task, destination_repo)

                elif cmd == 'p' or cmd == 'prio':
                    if len(args) == 4:
                        prio = priorities_map[args]
                    else:
                        prio = args

                    if prio not in priorities_map.values():
                        # Try to set
                        self.logger.warning(
                            'Try to set an non supported priority : %s' % prio)
                        continue

                    prio = "priority_%s" % prio
                    if prio not in issue.labels:
                        labels = issue.labels
                        labels.append(prio)
                        issue.labels = labels
                else:
                    self.logger.warning("command %s not supported" % cmd)
