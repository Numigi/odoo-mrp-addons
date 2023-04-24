FROM quay.io/numigi/odoo-public:12.latest
LABEL maintainer="contact@numigi.com"

USER root

COPY .docker_files/requirements.txt .
RUN pip3 install -r requirements.txt

ENV THIRD_PARTY_ADDONS /mnt/third-party-addons
RUN mkdir -p "${THIRD_PARTY_ADDONS}" && chown -R odoo "${THIRD_PARTY_ADDONS}"
COPY ./gitoo.yml /gitoo.yml
RUN gitoo install-all --conf_file /gitoo.yml --destination "${THIRD_PARTY_ADDONS}"

USER odoo

COPY mrp_bom_cost_scheduled_action /mnt/extra-addons/mrp_bom_cost_scheduled_action
COPY mrp_cost /mnt/extra-addons/mrp_cost
COPY mrp_timesheet /mnt/extra-addons/mrp_timesheet
COPY mrp_work_order_calendar_customer /mnt/extra-addons/mrp_work_order_calendar_customer

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo
