def officer_profile_context(request):
    """
    Injects officer profile details into every template context.
    Avoids chaining long template variable lookups in base.html.
    """
    officer_data = {
        'nav_name': '',
        'nav_designation': 'Officer',
        'nav_division': 'Not Assigned',
        'nav_station': 'Not Assigned',
        'nav_badge': 'N/A',
        'nav_phone': '',
        'nav_email': '',
    }

    if not request.user.is_authenticated:
        return officer_data

    # Name
    full_name = (request.user.first_name + ' ' + request.user.last_name).strip()
    officer_data['nav_name'] = full_name if full_name else request.user.username

    # Contact
    officer_data['nav_phone'] = request.user.phone_number or 'No Phone'
    officer_data['nav_email'] = request.user.email or 'No Email'

    if request.user.user_type == 'OFFICER':
        try:
            profile = request.user.officer_profile
            officer_data['nav_designation'] = profile.designation or 'Officer'
            officer_data['nav_badge'] = profile.badge_number or 'N/A'

            # Station
            try:
                if profile.station:
                    officer_data['nav_station'] = profile.station.name
            except Exception:
                pass

            # Division: try user.division first, then fall back to station's division
            division = None
            try:
                division = request.user.division
            except Exception:
                pass

            if not division:
                try:
                    division = profile.station.division
                except Exception:
                    pass

            if division:
                officer_data['nav_division'] = division.name
        except Exception:
            pass

    return officer_data
