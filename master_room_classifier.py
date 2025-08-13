#!/usr/bin/env python3
"""
Master Room Classifier
Kết hợp ARR, DEP, và GIH files theo logic nghiệp vụ đúng:
- File ARR: Xác định ARR (khách check-in ngày chia lịch)  
- File DEP: Xác định DEP (khách check-out ngày chia lịch)
- File GIH: Xác định OD (khách ở qua đêm) + bổ sung ARR nếu có
"""

import os
import re
import subprocess
from datetime import datetime, timedelta


def get_schedule_date_input():
    """Nhập ngày chia lịch từ user"""
    print("📅 NHẬP NGÀY CHIA LỊCH")
    print("=" * 40)
    
    tomorrow = datetime.now() + timedelta(days=1)
    default_date = tomorrow.strftime("%d-%m-%y")
    
    while True:
        date_input = input(f"Nhập ngày chia lịch (DD-MM-YY) [mặc định: {default_date}]: ").strip()
        
        if not date_input:
            date_input = default_date
            
        try:
            schedule_date = datetime.strptime(date_input, "%d-%m-%y")
            print(f"✅ Ngày chia lịch: {schedule_date.strftime('%d-%m-%y')}")
            return schedule_date.strftime("%d-%m-%y")
        except ValueError:
            print("❌ Format ngày không đúng! Vui lòng nhập theo format DD-MM-YY")


def pdf_to_text(pdf_path):
    """Convert PDF thành text sử dụng pdftotext"""
    text_path = pdf_path.replace('.pdf', '.txt').replace('.PDF', '.txt')
    
    try:
        cmd = ['pdftotext', '-layout', pdf_path, text_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and os.path.exists(text_path):
            return text_path
        else:
            print(f"❌ pdftotext error for {pdf_path}: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error converting {pdf_path}: {e}")
        return None


def extract_rooms_from_arr_dep(pdf_path, file_type):
    """
    Trích xuất số phòng từ file ARR/DEP
    Sử dụng crop method đã test trước đó
    """
    print(f"📄 Processing {file_type} file: {pdf_path}")
    
    # Convert to text first
    text_path = pdf_to_text(pdf_path)
    if not text_path:
        return []
    
    try:
        with open(text_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Extract room numbers - tìm 4 digit numbers đầu dòng hoặc trong dòng
        rooms = []
        for line in lines:
            line_clean = line.strip()
            if line_clean:
                # Tìm room numbers (4 digits)
                room_matches = re.findall(r'\b(\d{4})\b', line_clean)
                for room in room_matches:
                    # Filter ra những số hợp lý làm room number (loại bỏ dates, etc)
                    if not re.match(r'^(19|20)\d{2}$', room):  # Không phải năm
                        rooms.append(room)
        
        # Remove duplicates and sort
        unique_rooms = sorted(list(set(rooms)))
        
        print(f"✅ {file_type}: Extracted {len(unique_rooms)} rooms")
        if unique_rooms:
            if len(unique_rooms) <= 10:
                print(f"   Rooms: {', '.join(unique_rooms)}")
            else:
                first_5 = ', '.join(unique_rooms[:5])
                last_5 = ', '.join(unique_rooms[-5:])
                print(f"   First 5: {first_5}")
                print(f"   Last 5:  {last_5}")
        
        return unique_rooms
        
    except Exception as e:
        print(f"❌ Error processing {file_type}: {e}")
        return []


def extract_rooms_from_gih(pdf_path, schedule_date):
    """
    Trích xuất và phân loại phòng từ file GIH
    - OD: Phòng ở qua đêm (không check-in/out ngày schedule)
    - ARR: Phòng check-in = schedule date (bổ sung cho file ARR)
    """
    print(f"📄 Processing GIH file: {pdf_path}")
    
    # Convert to text
    text_path = pdf_to_text(pdf_path)
    if not text_path:
        return {'ARR': [], 'OD': []}
    
    try:
        with open(text_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Find header để xác định column positions
        header_line_idx = None
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if ('room' in line_lower and 'arr' in line_lower and 'dep' in line_lower):
                header_line_idx = i
                break
        
        # Extract room data
        room_data = []
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if not line_clean:
                continue
            
            # Look for lines starting with room number
            room_match = re.match(r'^(\d{4})', line_clean)
            
            if room_match:
                room_number = room_match.group(1)
                
                # Look for dates in current line (format: DD-MM-YY)
                dates_found = re.findall(r'\b(\d{2}-\d{2}-\d{2})\b', line_clean)
                
                if len(dates_found) >= 2:
                    checkin_date = dates_found[0]
                    checkout_date = dates_found[1]
                    
                    room_data.append({
                        'room': room_number,
                        'checkin': checkin_date,
                        'checkout': checkout_date
                    })
        
        # Remove duplicates
        seen_rooms = set()
        unique_room_data = []
        
        for data in room_data:
            room_key = f"{data['room']}_{data['checkin']}_{data['checkout']}"
            if room_key not in seen_rooms:
                seen_rooms.add(room_key)
                unique_room_data.append(data)
        
        # Classify rooms according to schedule date
        gih_arr_rooms = []  # Additional ARR from GIH
        gih_od_rooms = []   # OD (over day) rooms
        
        for room_info in unique_room_data:
            room = room_info['room']
            checkin = room_info['checkin']
            checkout = room_info['checkout']
            
            if checkin == schedule_date:
                # Check-in = schedule date → Additional ARR
                gih_arr_rooms.append(room)
            elif checkout == schedule_date:
                # Check-out = schedule date → Skip (handled by DEP file)
                pass
            else:
                # Over day → OD
                gih_od_rooms.append(room)
        
        # Remove duplicates and sort
        gih_arr_rooms = sorted(list(set(gih_arr_rooms)))
        gih_od_rooms = sorted(list(set(gih_od_rooms)))
        
        print(f"✅ GIH: Extracted {len(unique_room_data)} total room records")
        print(f"   Additional ARR: {len(gih_arr_rooms)} rooms")
        print(f"   OD (Over Day):  {len(gih_od_rooms)} rooms")
        
        return {
            'ARR': gih_arr_rooms,
            'OD': gih_od_rooms
        }
        
    except Exception as e:
        print(f"❌ Error processing GIH: {e}")
        return {'ARR': [], 'OD': []}


def master_room_classification(arr_file, dep_file, gih_file, schedule_date):
    """
    Master function để phân loại phòng từ cả 3 files
    """
    print(f"🏨 MASTER ROOM CLASSIFICATION")
    print(f"Schedule Date: {schedule_date}")
    print("=" * 60)
    
    # Step 1: Extract ARR rooms from ARR file
    print("\n📋 STEP 1: Processing ARR file")
    arr_rooms = extract_rooms_from_arr_dep(arr_file, "ARR") if os.path.exists(arr_file) else []
    
    # Step 2: Extract DEP rooms from DEP file  
    print("\n📋 STEP 2: Processing DEP file")
    dep_rooms = extract_rooms_from_arr_dep(dep_file, "DEP") if os.path.exists(dep_file) else []
    
    # Step 3: Extract OD + additional ARR from GIH file
    print("\n📋 STEP 3: Processing GIH file")
    gih_result = extract_rooms_from_gih(gih_file, schedule_date) if os.path.exists(gih_file) else {'ARR': [], 'OD': []}
    
    # Step 4: Combine results
    print("\n📋 STEP 4: Combining results")
    
    # Combine ARR (from ARR file + GIH additional)
    combined_arr = list(set(arr_rooms + gih_result['ARR']))
    combined_arr.sort()
    
    # DEP (from DEP file only)
    combined_dep = dep_rooms.copy()
    combined_dep.sort()
    
    # OD (from GIH only)
    combined_od = gih_result['OD']
    
    return {
        'ARR': combined_arr,
        'DEP': combined_dep, 
        'OD': combined_od
    }


def edit_room_list_manual(category, current_rooms):
    """Cho phép edit thủ công danh sách phòng"""
    category_names = {
        'ARR': 'ARRIVAL (Khách đến)',
        'DEP': 'DEPARTURE (Khách đi)', 
        'OD': 'OVER DAY (Khách ở qua đêm)'
    }
    
    print(f"\n✏️  EDIT {category} - {category_names[category]}")
    print("=" * 50)
    print(f"Hiện tại có {len(current_rooms)} phòng")
    
    if current_rooms:
        print("Danh sách hiện tại:")
        current_str = ', '.join(current_rooms)
        print(f"     {current_str}")
    
    print("\n🔧 TUỲ CHỌN:")
    print("1. Giữ nguyên")
    print("2. Thêm phòng")
    print("3. Xóa phòng") 
    print("4. Thay thế toàn bộ")
    print("5. Xóa tất cả")
    
    choice = input("\nChọn (1-5): ").strip()
    
    if choice == '1':
        return current_rooms
    
    elif choice == '2':
        add_rooms = input("Nhập phòng cần thêm (cách nhau bởi dấu phẩy): ").strip()
        if add_rooms:
            new_rooms = [room.strip() for room in add_rooms.split(',') if room.strip()]
            updated_rooms = list(set(current_rooms + new_rooms))
            updated_rooms.sort()
            print(f"✅ Đã thêm {len(new_rooms)} phòng. Tổng: {len(updated_rooms)} phòng")
            return updated_rooms
        return current_rooms
    
    elif choice == '3':
        remove_rooms = input("Nhập phòng cần xóa (cách nhau bởi dấu phẩy): ").strip()
        if remove_rooms:
            rooms_to_remove = [room.strip() for room in remove_rooms.split(',') if room.strip()]
            updated_rooms = [room for room in current_rooms if room not in rooms_to_remove]
            removed_count = len(current_rooms) - len(updated_rooms)
            print(f"✅ Đã xóa {removed_count} phòng. Còn lại: {len(updated_rooms)} phòng")
            return updated_rooms
        return current_rooms
    
    elif choice == '4':
        replace_rooms = input("Nhập toàn bộ danh sách phòng mới (cách nhau bởi dấu phẩy): ").strip()
        if replace_rooms:
            new_rooms = [room.strip() for room in replace_rooms.split(',') if room.strip()]
            new_rooms.sort()
            print(f"✅ Đã thay thế. Tổng: {len(new_rooms)} phòng")
            return new_rooms
        return current_rooms
    
    elif choice == '5':
        confirm = input("Xác nhận xóa tất cả phòng? (y/N): ").strip().lower()
        if confirm == 'y':
            print("✅ Đã xóa tất cả phòng")
            return []
        return current_rooms
    
    else:
        print("Lựa chọn không hợp lệ. Giữ nguyên danh sách.")
        return current_rooms


def manual_edit_workflow(classifications):
    """Workflow để edit manual các danh sách phòng"""
    print(f"\n🔧 MANUAL EDIT WORKFLOW")
    print("=" * 50)
    
    edited_classifications = {}
    
    for category in ['ARR', 'DEP', 'OD']:
        current_rooms = classifications.get(category, [])
        edited_rooms = edit_room_list_manual(category, current_rooms.copy())
        edited_classifications[category] = edited_rooms
    
    return edited_classifications


def display_final_results(classifications, title="FINAL CLASSIFICATION RESULTS"):
    """Hiển thị kết quả cuối cùng với danh sách đầy đủ"""
    print(f"\n🎯 {title} (FULL LIST)")
    print("=" * 60)
    
    total_rooms = 0
    for category, rooms in classifications.items():
        count = len(rooms)
        total_rooms += count
        
        category_names = {
            'ARR': 'ARRIVAL (Khách đến)',
            'DEP': 'DEPARTURE (Khách đi)', 
            'OD': 'OVER DAY (Khách ở qua đêm)'
        }
        
        print(f"\n{category}: {count:3d} phòng - {category_names[category]}")
        print("-" * 40)
        
        if rooms:
            # Display all rooms, 10 per line for better readability
            for i in range(0, len(rooms), 10):
                line_rooms = rooms[i:i+10]
                print(f"     {', '.join(line_rooms)}")
        else:
            print("     (Không có phòng)")
    
    print(f"\n📊 SUMMARY: Total {total_rooms} rooms processed")


def export_for_web(classifications):
    """Xuất định dạng cho web (comma-separated)"""
    print(f"\n🌐 WEB EXPORT FORMAT")
    print("=" * 50)
    
    for category, rooms in classifications.items():
        category_names = {
            'ARR': 'ARRIVAL',
            'DEP': 'DEPARTURE', 
            'OD': 'OVER DAY'
        }
        
        print(f"\n{category} ({category_names[category]}):")
        if rooms:
            rooms_str = ', '.join(rooms)
            print(rooms_str)
        else:
            print('(empty)')
    
    # Also create a single line format
    print(f"\n📋 SINGLE LINE FORMAT:")
    all_data = []
    for category, rooms in classifications.items():
        if rooms:
            all_data.append(f"{category}: {', '.join(rooms)}")
    
    if all_data:
        print(' | '.join(all_data))


def main():
    """Main function"""
    print("🏨 HOTEL ROOM CLASSIFICATION SYSTEM")
    print("=" * 70)
    
    # Define file paths
    arr_file = "arr14.08.25 (1).PDF"
    dep_file = "dep14.08.25 (1).PDF"
    gih_file = "GIH01103 Guests in House by Room (2).PDF"
    
    # Check if files exist
    files_status = []
    for filename, filepath in [("ARR", arr_file), ("DEP", dep_file), ("GIH", gih_file)]:
        exists = os.path.exists(filepath)
        files_status.append((filename, filepath, exists))
        status = "✅" if exists else "❌"
        print(f"{status} {filename}: {filepath}")
    
    # Get schedule date
    schedule_date = get_schedule_date_input()
    
    # Process all files
    classifications = master_room_classification(arr_file, dep_file, gih_file, schedule_date)
    
    # Display initial results
    display_final_results(classifications, "INITIAL CLASSIFICATION RESULTS")
    
    # Ask if user wants to edit manually
    print(f"\n❓ CÓ MUỐN CHỈNH SỬA THỦ CÔNG?")
    print("=" * 40)
    print("1. Không, sử dụng kết quả tự động")
    print("2. Có, chỉnh sửa từng danh sách")
    
    edit_choice = input("\nChọn (1-2): ").strip()
    
    if edit_choice == '2':
        # Manual edit workflow
        final_classifications = manual_edit_workflow(classifications)
        
        # Display edited results
        display_final_results(final_classifications, "FINAL EDITED RESULTS")
    else:
        final_classifications = classifications
        print("✅ Sử dụng kết quả tự động")
    
    # Export options
    print(f"\n💾 XUẤT DỮ LIỆU")
    print("=" * 30)
    print("1. Xuất định dạng cho web")
    print("2. Kết thúc")
    
    export_choice = input("\nChọn (1-2): ").strip()
    
    if export_choice == '1':
        export_for_web(final_classifications)
    
    return final_classifications


if __name__ == "__main__":
    result = main()
