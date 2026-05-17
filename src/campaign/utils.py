def convert_views_to_int(view_string):
    """
    Yeh function '1.9k', '1.5M' jaise text ko pure numbers (integers) mein convert karega
    taaki database crash na ho aur math calculation sahi rahe.
    """
    # 1. Text ko chota (lowercase) karein aur commas (,) hata dein
    view_string = str(view_string).lower().replace(',', '').strip()
    
    # 2. Agar K (Thousand) hai
    if 'k' in view_string:
        return int(float(view_string.replace('k', '')) * 1000)
        
    # 3. Agar M (Million) hai
    elif 'm' in view_string:
        return int(float(view_string.replace('m', '')) * 1000000)
        
    # 4. Agar L (Lakh) hai 
    elif 'l' in view_string:
        return int(float(view_string.replace('l', '')) * 100000)
        
    # 5. Agar B (Billion) hai
    elif 'b' in view_string:
        return int(float(view_string.replace('b', '')) * 1000000000)
        
    # 6. if no letter ("450" views)
    else:
        try:
            return int(float(view_string))
        except ValueError:
            return 0