# =========================================================================================#
# OWNER : Aakaash Ramnath Sankar
# DATE : 2020-10-30
# FILE : app.py
# DEVELOPER : Aakaash Ramnath Sankar
# DESCRIPTION : Generate payslips in PDF format using Excel file(s) as an input
# =========================================================================================#

import logging
from fpdf import FPDF, HTMLMixin

logging.basicConfig(
    format="=>%(levelname)s : %(asctime)s : %(filename)s : %(funcName)s |::| %(message)s",
    level=logging.DEBUG,
)


html = """
<html><head>
</head>
<body>
<h2 align="center" style="color:black;"><b>Payslip for the month of {month}/{year}</b></h2>
<br><br><br>
<font size="10" face="Courier New" >
<table border="0" align="center" width="100%" cellpadding="8">
<thead>
<tr>
<th width = "20%"></th>
<th width = "30%"></th>
<th width = "20%"></th>
<th width = "30%"></th>
</tr>
</thead>
<tbody>
<tr>
<td align="left">Emp ID</td>
<td align="left">{emp_id}</td>
<td align="left">Employee Name</td>
<td align="left">{emp_name}</td>
</tr>
<tr>
<td align="left">DOJ</td>
<td align="left">{doj}</td>
<td align="left">Pay Days</td>
<td align="left">{pay_days}</td>
</tr>
<tr>
<td align="left">Department</td>
<td align="left">{department}</td>
<td align="left">Designation</td>
<td align="left">{designation}</td>
</tr>
<tr>
<td align="left">A/c No.</td>
<td align="left">{acc_number}</td>
<td align="left">Branch</td>
<td align="left">{branch}</td>
</tr>
<tr>
<td align="left">IFSC</td>
<td align="left">{mode_of_pay}</td>
<td align="left">Bank</td>
<td align="left">{pan_number}</td>
</tr>
<tr>
<td align="left">PF UAN</td>
<td align="left">{pf_uan}</td>
<td align="left">PAN</td>
<td align="left">{esi_number}</td>
</tr>
<tr>
<td colspan="4"> </td>
</tr>
</tr>
<tr>
<td colspan="4"> </td>
</tr>
</tbody>
</table>
</font>
<br>
<font size="8" face="Courier New" >
<table border="1" align="center" width="100%" cellpadding="8">
<tbody><tr>
<th width="14%">Earnings</th>
<th width="17%">For the month</th>
<th width="17%">YTD</th>
<th width="4%" rowspan="8"> </th>
<th width="14%">Deduction</th>
<th width="17%">For the month</th>
<th width="17%">YTD</th>
</tr>
<tr>
<td align="left">Basic</td>
<td align="right">{ftm_basic}</td>
<td align="right">{ytd_basic}</td>
<td> </td>
<td align="left">EPFO</td>
<td align="right">{dftm_epfo}</td>
<td align="right">{dytd_epfo}</td>
</tr>
<tr>
<td align="left">HRA</td>
<td align="right">{ftm_hra}</td>
<td align="right">{ytd_hra}</td>
<td> </td>
<td align="left">ESIC</td>
<td align="right">{dftm_esic}</td>
<td align="right">{dytd_esic}</td>
</tr>
<tr>
<td align="left">DA</td>
<td align="right">{ftm_da}</td>
<td align="right">{ytd_da}</td>
<td> </td>
<td align="left">TDS</td>
<td align="right">{dftm_tds}</td>
<td align="right">{dytd_tds}</td>
</tr>
<tr>
<td align="left">Other Allow</td>
<td align="right">{ftm_otherallow}</td>
<td align="right">{ytd_otherallow}</td>
<td> </td>
<td align="left">Transport</td>
<td align="right">{dftm_transport}</td>
<td align="right">{dytd_transport}</td>
</tr>
<tr>
<td align="left">OT</td>
<td align="right">{ftm_ot}</td>
<td align="right">{ytd_ot}</td>
<td> </td>
<td align="left"> </td>
<td align="left"> </td>
<td align="left"> </td>
</tr>
<tr>
<th align="left">Earned Gross</th>
<th>{ftm_gross}</th>
<th>{ytd_gross}</th>
<td> </td>
<th aligh="left">Gross Deduction</th>
<th>{dftm_gross}</th>
<th>{dytd_gross}</th>
</tr>
<tr height="30px">
<th colspan="7" colwidth="10"> </th>
</tr>
<tr>
<th>Net For the month</th>
<th colspan="2">{ftm_netpay}</th>
<th> </th>
<th>Net YTD</th>
<th colspan="2">{ytd_netpay}</th>
</tr>
<tr height="45px">
<th>In words</th>
<th colspan="6">INR {ftm_netpay_words} only</th>
</tr>
<tr>
<th>In words</th>
<th colspan="6">INR {ytd_netpay_words} only</th>
</tr>
<tr>
<th align="left" colspan="7" height="80"> </th>
</tr>
</tbody></table>
</font>
</body></html>
"""


class MyFPDF(FPDF, HTMLMixin):
    FPDF(format="A4")
    pass


print("===================")
obj = MyFPDF()
obj.add_page()
print("===================")
obj.image(r"./utility/payslip_bg.png", x=0, y=0, w=210)
# obj.set_fill_color(237, 240, 242)
obj.ln(43)
print("===================")
# obj.set_font("Arial", "B", 12)
# obj.cell(w=200, h=10, txt="----------------", ln=1, align="C")
print("===================")
# obj.set_font("Arial", "B", 10)
obj.write_html(html)
# obj.write_html(html1)
print("===================")
obj.output("outfile.pdf")