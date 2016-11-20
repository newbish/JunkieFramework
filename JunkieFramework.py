class Settings(object):
    def __init__(self,
                 email_sender="hypadmin@epmjunkie.com",
                 email_smtp_host="localhost",
                 email_smtp_port=25,
                 email_smtp_password=None,
                 email_smtp_tls=False):
        self.email_sender = email_sender
        self.email_smtp_password = email_smtp_password
        self.email_smtp_host = email_smtp_host
        self.email_smtp_tls = email_smtp_tls
        self.email_smtp_port = email_smtp_port


class Core(object):
    class _Log:
        def __init__(self, context, api, seperator=":\t", delimiter="\n"):
            self._context = context
            self.api = api
            self.seperator = seperator
            self.delim = delimiter


        def _parse(self, obj, seperator=None, delimiter=None):
            if not delimiter:
                delimiter = self.delim
            if not seperator:
                seperator = self.seperator
            return delimiter.join(["%s%s%s" % (key, seperator, value) for (key, value) in sorted(obj.items())])

        def object(self, obj, prefix="Object: ", seperator=None, delimiter=None):
            if obj:
                return "%(prefix)s%(list)s" % {"prefix": prefix, "list": self._parse(obj, seperator, delimiter)}
            return "%sEmpty" % prefix

        def context(self):
            if self.context:
                self.api.logDebug(self.object(self._context, prefix="FDM Context:\n"))
            else:
                self.api.logWarn(self.object(self._context, prefix="FDM Context: "))

    class _Email:
        def __init__(self, settings):
            self.sender = settings.email_sender
            self.host = settings.email_smtp_host
            self.port = settings.email_smtp_port
            self.password = settings.email_smtp_password
            self.tls = settings.email_smtp_tls

        # Handles sending email with optional attachments
        '''
        Sample usage:
        subject = "Data load has started"
        body = "Data load for location has started."
        recipients = can be a array ["hypadmin@epmjunkie.com","testing@epmjunkie.com"] or comma delimited list
        send(recipients=recipients, subject=subject, body=body)
        '''
        def send(self, recipients, body, subject="Test Message", attachment=[], sender=None,
                     host=None, port=None, password=None, tls=None):
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            if not sender:
                sender = self.sender
            if not host:
                host = self.host
            if not port:
                port = self.port
            if not password:
                password = self.password
            if tls is None:
                tls = self.tls


            # Catch missing emails
            if len(recipients) == 0:
                recipients = sender
                recipients = [recipients]
                subject = "Invalid Recipients - " + subject
            else:
                # Check if its a comma delimited string already
                if "," in recipients:
                    recipients = [x.strip() for x in recipients.split(",")]
                else:
                    recipients = [recipients]

            client = smtplib.SMTP(host, port)
            if tls:
                client.ehlo()
                client.starttls()
                client.ehlo()
            if password:
                client.login(sender, password)
            message = MIMEMultipart()
            message["From"] = sender
            message["To"] = ', '.join(recipients)
            message["Subject"] = subject
            for item in attachment:
                message.attach(item)
            message.attach(MIMEText(body))
            client.sendmail(sender, recipients, message.as_string())
            client.quit()
            client.close()

        # Handles creating attachment for emailing
        def create_attachment(self, path, name):
            import mimetypes
            from email.mime.audio import MIMEAudio
            from email.mime.base import MIMEBase
            from email.mime.image import MIMEImage
            from email.mime.text import MIMEText
            from email import encoders
            if len(name) > 0 and len(path) > 0:
                contentType = mimetypes.guess_type(path)[0]

                if contentType is None:
                    contentType = "text/plain"

                maintype, subtype = contentType.split("/", 1)

                f = open(path)
                if maintype == "text":
                    attachment = MIMEText(f.read(), _subtype=subtype)
                elif maintype == "image":
                    attachment = MIMEImage(f.read(), _subtype=subtype)
                elif maintype == "audio":
                    attachment = MIMEAudio(f.read(), _subtype=subtype)
                else:
                    attachment = MIMEBase(_maintype=maintype, _subtype=subtype)
                    attachment.set_payload(f.read())
                encoders.encode_base64(attachment)
                f.close()
                attachment.add_header("Content-Disposition", "attachment", filename=name)

                return attachment
            return None

    def __init__(self, context, api, settings=Settings()):
        self._context = context
        self._api = api
        self.settings = settings
        self.email = self._Email(settings=settings)
        self.log = self._Log(context, api)

    def get_context_value(self, name):
        return str(self._context[name])

    @property
    def application_id(self):
        return self.getContextValue("APPID")

    @property
    def batch_script_directory(self):
        return self.getContextValue("BATCHSCRIPTDIR")

    @property
    def category(self):
        return self.getContextValue("CATNAME")

    @property
    def category_key(self):
        return self.getContextValue("CATKEY")

    @property
    def check_status(self):
        return self.getContextValue("CHKSTATUS")

    @property
    def epm_home(self):
        return self.getContextValue("EPMORACLEHOME")

    @property
    def epm_instance_home(self):
        return self.getContextValue("EPMORACLEINSTANCEHOME")

    @property
    def export_flag(self):
        return self.getContextValue("EXPORTFLAG")

    @property
    def export_mode(self):
        return self.getContextValue("EXPORTMODE")

    @property
    def export_status(self):
        return self.getContextValue("EXPSTATUS")

    @property
    def file_directory(self):
        return self.getContextValue("FILEDIR")

    @property
    def file_name(self):
        return self.getContextValue("FILENAME")

    @property
    def import_flag(self):
        return self.getContextValue("IMPORTFLAG")

    @property
    def import_format(self):
        return self.getContextValue("IMPORTFORMAT")

    @property
    def import_status(self):
        return self.getContextValue("IMPSTATUS")

    @property
    def inbox_directory(self):
        return self.getContextValue("INBOXDIR")

    @property
    def load_id(self):
        return self.getContextValue("LOADID")

    @property
    def location_key(self):
        return self.getContextValue("LOCKEY")

    @property
    def location(self):
        return self.getContextValue("LOCNAME")

    @property
    def multi_period_load(self):
        return self.getContextValue("MULTIPERIODLOAD")

    @property
    def outbox_directory(self):
        return self.getContextValue("OUTBOXDIR")

    @property
    def period(self):
        return self.getContextValue("PERIODNAME")

    @property
    def period_key(self):
        return self.getContextValue("PERIODKEY")

    @property
    def process_status(self):
        return self.getContextValue("PROCESSSTATUS")

    @property
    def rule(self):
        return self.getContextValue("RULENAME")

    @property
    def rule_id(self):
        return self.getContextValue("RULEID")

    @property
    def script_directory(self):
        return self.getContextValue("SCRIPTSDIR")

    @property
    def source_name(self):
        return self.getContextValue("SOURCENAME")

    @property
    def source_type(self):
        return self.getContextValue("SOURCETYPE")

    @property
    def target_app(self):
        return self.getContextValue("TARGETAPPNAME")

    @property
    def target_app_db(self):
        return self.getContextValue("TARGETAPPDB")

    @property
    def target_app_id(self):
        return self.getContextValue("APPID")

    @property
    def validation_status(self):
        return self.getContextValue("VALSTATUS")