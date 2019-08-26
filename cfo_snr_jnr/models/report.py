from odoo import fields, models, api


class TimeTablereport(models.AbstractModel):
    _name = 'report.cfo_snr_jnr.report_timetable'

    @api.model
    def get_report_values(self, docids, data=None):
        print("\n\n\n docids",docids)
        print("\n\n\n data>>>>", data)
        return {
            'docids':docids,
            'data': data,
            'doc_model': 'cfo.time.table',
        }