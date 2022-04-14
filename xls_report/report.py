# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import xlwt
import base64
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta

from cStringIO import StringIO


class GenericReportWiz(models.TransientModel):
    """Generic Report Wizard"""
    _name = "generic.report.wiz"

    date_param = fields.Date("Start Date")
    file = fields.Binary('File')
    file_name = fields.Char(string='File Name', size=128)

    @api.multi
    def generic_report_download(self):
        """
            This method is used to download the Generic Report.
        """
        date_param = datetime.strptime(self.date_param, '%Y-%m-%d')
        date_start = date_param.strftime('%Y-%m-01')
        date_end = (date_param + relativedelta(months=1)).strftime('%Y-%m-01')
        selected_records = self.env['some.model'].search(
                                                                [
                                                                    ('some_date', '>=', date_start),
                                                                    ('some_date', '<', date_end),
                                                                ]
                                                            )

        report_name = 'Generic Report'
        file = StringIO()
        workbook = xlwt.Workbook()  
        sheet = workbook.add_sheet(report_name, cell_overwrite_ok=True)
        font = xlwt.Font()
        font.bold = True
        xlwt.add_palette_colour("custom_colour", 0x21)
        workbook.set_colour_RGB(0x21, 255, 182, 193)
        bold_style = xlwt.XFStyle()
        bold_style.font = font

        style_base = 'font: height 210, name Calibri; align: wrap off;'
        style_white_text_on_blue = 'colour white; pattern: pattern solid, fore_colour light_blue;'
        style_black_text_on_gray = 'bold 1; pattern: pattern solid, fore_colour gray25;'
        style_black_text_on_paleblue = 'bold 1; pattern: pattern solid, fore_colour pale_blue;'
        style_left = 'horiz left;'
        style_center = 'horiz center;'
        style_right = 'horiz right;'

        report_header_style_left = xlwt.easyxf(style_base + style_black_text_on_gray + style_left)
        report_header_style_center = xlwt.easyxf(style_base + style_black_text_on_gray + style_center)
        report_header_style_right = xlwt.easyxf(style_base + style_black_text_on_gray + style_right)
        report_header_alt_style_left = xlwt.easyxf(style_base + style_black_text_on_paleblue + style_left)
        report_header_alt_style_center = xlwt.easyxf(style_base + style_black_text_on_paleblue + style_center)
        report_header_alt_style_right = xlwt.easyxf(style_base + style_black_text_on_paleblue + style_right)
        
        header_style_left = xlwt.easyxf(style_base + style_white_text_on_blue + style_left)
        header_style_center = xlwt.easyxf(style_base + style_white_text_on_blue + style_center)
        header_style_right = xlwt.easyxf(style_base + style_white_text_on_blue + style_right)
        
        content_style_left = xlwt.easyxf(style_base + style_left)
        content_style_center = xlwt.easyxf(style_base + style_center)
        content_style_right = xlwt.easyxf(style_base + style_right)

        sheet.col(0).width = 700*12
        sheet.row(0).height = 80*5
        sheet.col(1).width = 700*12
        sheet.row(1).height = 80*5

        # Write header to define date, slot and location
        sheet.write(0, 0, 'Generic Report', report_header_style_left)
        sheet.write(0, 1, '', report_header_style_left)
        sheet.write(2, 0, 'Year', report_header_style_center)
        sheet.write(2, 1, date_param.strftime('%Y'), report_header_alt_style_center)
        sheet.write(1, 0, 'Month', report_header_style_center)
        sheet.write(1, 1, date_param.strftime('%B'), report_header_alt_style_center)
        insured_col = 0
        def size_insured():
            col = insured_col
            sheet.col(col+0).width = 300*12
            sheet.col(col+1).width = 1000*12
            sheet.col(col+2).width = 500*12

        def write_insured_headers(row):
            col = insured_col
            sheet.write(row,col + 0, 'Employee No', style=header_style_center)
            sheet.write(row,col + 1, 'Full Name', style=header_style_left)
            sheet.write(row,col + 2, 'DOB(YYYY-MM-DD)', style=header_style_center)

        def write_insured(record, row):
            col = insured_col
            sheet.write(row, col + 0, record.employee_id.number if record.employee_id else '', style=content_style_center)
            sheet.write(row, col + 1, record.employee_id.name if record.employee_id else '', style=content_style_left)
            sheet.write(row, col + 2, record.employee_id.dob if record.employee_id else '', style=content_style_center)

        size_insured()

        write_insured_headers(3)
        sheet.row(3).height = 120*5
        row = 4
        for record in selected_records:
            write_insured(record,row)
            row += 1

        workbook.save(file)
        file.seek(0)
        out = base64.encodestring(file.read())
        file_name = report_name + '-' + \
            date_param.strftime('%Y') + '-' + \
            date_param.strftime('%B') + '.xls'
        self.write({'file': out, 'file_name': file_name})

        return {
            'name': 'Generic Report',
            'res_model': 'generic.report.wiz',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'nodestroy': True,
            'res_id': self.id,
        }
