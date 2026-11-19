"""
Page: Organisation Management
Allows selecting and switching organisations, viewing and editing profiles,
managing departments, and assigning user memberships.
"""

from typing import Any
import streamlit as st
from database.connection import get_db_context
from database.models import Organisation, Department, User, OrganisationMembership
from modules.organisation import (
    get_user_organisations,
    create_organisation,
    get_organisation_departments,
    create_department,
    add_user_to_organisation,
)
from modules.authentication import check_permission
from utils.calculations import format_currency
import config


def render_organisations_page(current_user: Any, current_org: Any) -> None:
    st.markdown("## 🏢 Organisation Management & Portfolio Profiles")
    st.markdown("Manage organizational structures, departmental cost centers, and user memberships.")

    with get_db_context() as db:
        user_orgs = get_user_organisations(db, current_user)
        
        tab_switch, tab_depts, tab_members, tab_new = st.tabs([
            "🔄 Active Organisation",
            "📑 Departmental Cost Centers",
            "👥 Team & Role Access",
            "➕ Create New Organisation"
        ])

        with tab_switch:
            st.markdown("### Select Active Organisation")
            st.write("All subsequent financial models, simulators, and predictions will isolate exclusively to this entity.")

            org_options = {org.id: f"{org.name} ({org.org_type})" for org in user_orgs}
            selected_id = st.selectbox(
                "Choose Organisation",
                options=list(org_options.keys()),
                format_func=lambda x: org_options[x],
                index=list(org_options.keys()).index(current_org.id) if current_org.id in org_options else 0,
            )

            if selected_id != current_org.id:
                if st.button("Switch Active Entity", type="primary"):
                    st.session_state["current_org_id"] = selected_id
                    st.success(f"Switched context to: {org_options[selected_id]}")
                    st.rerun()

            # Profile Details Card
            st.markdown("---")
            st.markdown("#### Entity Profile")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Entity Name:** {current_org.name}")
                st.write(f"**Industry Category:** {current_org.org_type}")
                st.write(f"**Currency:** {current_org.currency}")
            with col2:
                st.write(f"**Annual Operating Budget:** {format_currency(current_org.annual_budget, current_org.currency)}")
                st.write(f"**Synthetic Sample Flag:** {'Yes (Synthetic)' if current_org.is_synthetic else 'No (Production)'}")
                st.write(f"**Description:** {current_org.description or 'None provided.'}")

        with tab_depts:
            st.markdown(f"### Departments for {current_org.name}")
            departments = get_organisation_departments(db, current_org.id)

            if departments:
                dept_rows = [{
                    "Department Name": d.name,
                    "Code": d.code,
                    "Annual Budget": format_currency(d.annual_budget, current_org.currency),
                    "Headcount": d.headcount,
                } for d in departments]
                st.dataframe(dept_rows, use_container_width=True)
            else:
                st.info("No departments configured yet.")

            if check_permission(current_user.role, "manage_departments"):
                with st.expander("➕ Add New Department"):
                    with st.form("form_add_dept"):
                        d_name = st.text_input("Department Name", placeholder="e.g. Supply Chain Logistics")
                        d_code = st.text_input("Department Code", placeholder="e.g. SCM-LOG")
                        d_budget = st.number_input("Annual Budget Allocation (₹)", min_value=0.0, step=100000.0, value=5000000.0)
                        d_headcount = st.number_input("Headcount", min_value=1, step=1, value=10)
                        submit_dept = st.form_submit_button("Register Department")

                        if submit_dept:
                            if not d_name or not d_code:
                                st.error("Department name and code are required.")
                            else:
                                create_department(db, current_org.id, d_name, d_code, d_budget, d_headcount)
                                st.success(f"Department '{d_name}' registered successfully.")
                                st.rerun()

        with tab_members:
            st.markdown(f"### Role-Based Access for {current_org.name}")
            memberships = db.query(OrganisationMembership).filter(
                OrganisationMembership.org_id == current_org.id
            ).all()

            mem_data = []
            for m in memberships:
                u = db.query(User).filter(User.id == m.user_id).first()
                if u:
                    mem_data.append({
                        "Username": u.username,
                        "Full Name": u.full_name,
                        "Email": u.email,
                        "Assigned Role": config.ROLE_DISPLAY_NAMES.get(m.role, m.role),
                    })
            st.dataframe(mem_data, use_container_width=True)

            if check_permission(current_user.role, "manage_org_members"):
                with st.expander("👤 Grant Organisation Access to Existing User"):
                    all_users = db.query(User).filter(User.is_active == True).all()
                    user_map = {u.id: f"{u.full_name} (@{u.username})" for u in all_users}
                    
                    with st.form("form_add_member"):
                        target_uid = st.selectbox("Select User", options=list(user_map.keys()), format_func=lambda x: user_map[x])
                        new_role = st.selectbox("Role", options=config.ALL_ROLES, format_func=lambda x: config.ROLE_DISPLAY_NAMES.get(x, x))
                        submit_member = st.form_submit_button("Assign Membership")

                        if submit_member:
                            success, msg = add_user_to_organisation(db, target_uid, current_org.id, new_role)
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

        with tab_new:
            st.markdown("### Create a New Independent Organisation")
            if not check_permission(current_user.role, "manage_org_profile"):
                st.warning("Only Organisation Administrators and Platform Administrators can create new organisations.")
            else:
                with st.form("form_create_org"):
                    new_name = st.text_input("Organisation Legal Name", placeholder="e.g. Apex Renewable Energy Ltd.")
                    new_type = st.selectbox("Sector / Entity Type", [
                        "Manufacturing & Industrial",
                        "Asset Management & Investment",
                        "Technology & Software",
                        "Educational Institution / Trust",
                        "Healthcare & Pharmaceuticals",
                        "Non-Governmental Organisation (NGO)",
                        "Other Commercial Business"
                    ])
                    new_budget = st.number_input("Annual Operating Budget (₹)", min_value=0.0, step=1000000.0, value=25000000.0)
                    new_desc = st.text_area("Description / Mission Statement", placeholder="Short overview of business activities...")
                    submit_create = st.form_submit_button("Create Organisation Entity", type="primary")

                    if submit_create:
                        if not new_name.strip():
                            st.error("Organisation name cannot be blank.")
                        else:
                            success, new_org, msg = create_organisation(
                                db,
                                name=new_name,
                                org_type=new_type,
                                annual_budget=new_budget,
                                currency="₹",
                                description=new_desc,
                                creator_user_id=current_user.id,
                                is_synthetic=False,
                            )
                            if success:
                                st.success(f"Organisation '{new_name}' created successfully!")
                                st.session_state["current_org_id"] = new_org.id
                                st.rerun()
                            else:
                                st.error(msg)
