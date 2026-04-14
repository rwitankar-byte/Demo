import requests
import sys
import json
import base64
from datetime import datetime
from pathlib import Path

class CropSenseAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {}
        
        if files is None:
            headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data)
                else:
                    response = requests.post(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Error: {response.text[:300]}")

            return success, response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test API root endpoint"""
        return self.run_test("API Root", "GET", "", 200)

    def test_status_endpoints(self):
        """Test status check endpoints"""
        # Test POST status
        success1, response1 = self.run_test(
            "Create Status Check",
            "POST",
            "status",
            200,
            data={"client_name": "test_client"}
        )
        
        # Test GET status
        success2, response2 = self.run_test(
            "Get Status Checks",
            "GET",
            "status",
            200
        )
        
        return success1 and success2

    def create_test_image(self):
        """Create a simple test image for classification"""
        # Create a simple 64x64 green leaf-like image using PIL
        try:
            from PIL import Image, ImageDraw
            import io
            
            # Create a 64x64 image with green background
            img = Image.new('RGB', (64, 64), color='lightgreen')
            draw = ImageDraw.Draw(img)
            
            # Draw a simple leaf shape
            draw.ellipse([10, 10, 54, 54], fill='green', outline='darkgreen')
            draw.ellipse([20, 20, 44, 44], fill='darkgreen')
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            return img_bytes.getvalue()
            
        except ImportError:
            # Fallback to a valid minimal PNG if PIL is not available
            # This is a 1x1 green pixel PNG
            png_data = base64.b64decode(
                'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
            )
            return png_data

    def test_classify_endpoint(self):
        """Test disease classification endpoint"""
        # Create test image
        test_image = self.create_test_image()
        
        files = {
            'file': ('test_leaf.png', test_image, 'image/png')
        }
        
        success, response = self.run_test(
            "Disease Classification",
            "POST",
            "classify",
            200,
            files=files
        )
        
        if success and isinstance(response, dict):
            # Validate response structure
            required_fields = ['label', 'confidence']
            for field in required_fields:
                if field not in response:
                    print(f"❌ Missing field in classification response: {field}")
                    return False
            
            # Validate data types
            if not isinstance(response['confidence'], (int, float)):
                print(f"❌ Confidence should be numeric, got: {type(response['confidence'])}")
                return False
                
            print(f"✅ Classification response valid: {response['label']} ({response['confidence']:.2f})")
        
        return success

    def test_advisory_endpoint(self):
        """Test treatment advisory endpoint"""
        # Test with sample data
        test_data = {
            "crop_name": "Tomato",
            "disease_label": "Tomato Leaf Spot",
            "confidence": 0.85,
            "image_base64": base64.b64encode(self.create_test_image()).decode('utf-8')
        }
        
        success, response = self.run_test(
            "Treatment Advisory",
            "POST",
            "advisory",
            200,
            data=test_data
        )
        
        if success and isinstance(response, dict):
            # Validate response structure
            required_fields = [
                'visible_symptoms', 'likely_cause', 'severity', 
                'treatment', 'preventive_measures', 'plain_language_advisory'
            ]
            for field in required_fields:
                if field not in response:
                    print(f"❌ Missing field in advisory response: {field}")
                    return False
            
            # Validate severity values
            valid_severities = ['Healthy', 'Mild', 'Moderate', 'Severe']
            if response['severity'] not in valid_severities:
                print(f"❌ Invalid severity value: {response['severity']}")
                return False
                
            print(f"✅ Advisory response valid: {response['severity']} severity")
        
        return success

    def test_advisory_multilanguage(self):
        """Test advisory endpoint with different languages"""
        base_data = {
            "crop_name": "Tomato",
            "disease_label": "Tomato — Early Blight",
            "confidence": 0.85,
            "image_base64": base64.b64encode(self.create_test_image()).decode('utf-8')
        }
        
        languages = [
            ("English", "en"),
            ("Hindi", "hi"), 
            ("Marathi", "mr")
        ]
        
        all_success = True
        
        for lang_name, lang_code in languages:
            test_data = {**base_data, "language": lang_code}
            
            success, response = self.run_test(
                f"Advisory - {lang_name}",
                "POST",
                "advisory",
                200,
                data=test_data
            )
            
            if success and isinstance(response, dict):
                print(f"✅ {lang_name} advisory generated successfully")
                # For non-English, check if response contains non-ASCII characters (indicating local language)
                if lang_code != "en":
                    advisory_text = response.get('plain_language_advisory', '')
                    if any(ord(char) > 127 for char in advisory_text):
                        print(f"✅ {lang_name} response contains local language characters")
                    else:
                        print(f"⚠️  {lang_name} response may not be in local language")
            else:
                all_success = False
                
        return all_success

    def test_history_endpoints(self):
        """Test history CRUD operations"""
        print(f"\n🔄 Testing History CRUD Operations...")
        
        # Test data for history record
        history_data = {
            "crop_name": "Tomato",
            "disease_label": "Tomato — Early Blight",
            "confidence": 0.85,
            "severity": "Moderate",
            "visible_symptoms": "Brown spots on leaves",
            "likely_cause": "Fungal infection",
            "treatment": "Apply fungicide spray",
            "preventive_measures": "Ensure proper ventilation",
            "plain_language_advisory": "Your tomato plant has early blight. Apply fungicide treatment.",
            "language": "en"
        }
        
        # Test 1: Save diagnosis to history
        save_success, save_response = self.run_test(
            "Save Diagnosis to History",
            "POST",
            "history",
            200,
            data=history_data
        )
        
        if not save_success:
            return False
            
        record_id = save_response.get('id') if isinstance(save_response, dict) else None
        if not record_id:
            print("❌ No record ID returned from save operation")
            return False
        
        # Test 2: Get history (should include our record)
        get_success, get_response = self.run_test(
            "Get History",
            "GET", 
            "history",
            200
        )
        
        if not get_success:
            return False
            
        if not isinstance(get_response, list):
            print("❌ History response should be a list")
            return False
            
        # Check if our record is in the history
        found_record = False
        for record in get_response:
            if record.get('id') == record_id:
                found_record = True
                print(f"✅ Saved record found in history: {record['disease_label']}")
                break
                
        if not found_record:
            print("❌ Saved record not found in history")
            return False
        
        # Test 3: Delete specific record
        delete_success, _ = self.run_test(
            f"Delete Specific Record ({record_id})",
            "DELETE",
            f"history/{record_id}",
            200
        )
        
        if not delete_success:
            return False
            
        # Test 4: Verify record was deleted
        verify_success, verify_response = self.run_test(
            "Verify Record Deleted",
            "GET",
            "history", 
            200
        )
        
        if verify_success and isinstance(verify_response, list):
            # Check that our record is no longer in the list
            still_exists = any(record.get('id') == record_id for record in verify_response)
            if still_exists:
                print("❌ Record still exists after deletion")
                return False
            else:
                print("✅ Record successfully deleted")
        
        # Test 5: Clear all history
        clear_success, _ = self.run_test(
            "Clear All History",
            "DELETE",
            "history",
            200
        )
        
        if not clear_success:
            return False
            
        # Test 6: Verify history is empty
        empty_success, empty_response = self.run_test(
            "Verify History Cleared",
            "GET",
            "history",
            200
        )
        
        if empty_success and isinstance(empty_response, list):
            if len(empty_response) == 0:
                print("✅ History successfully cleared")
            else:
                print(f"⚠️  History not completely cleared, {len(empty_response)} records remain")
        
        return save_success and get_success and delete_success and clear_success

    def test_end_to_end_flow(self):
        """Test complete end-to-end flow"""
        print(f"\n🔄 Testing End-to-End Flow...")
        
        # Step 1: Classify image
        test_image = self.create_test_image()
        files = {'file': ('test_leaf.png', test_image, 'image/png')}
        
        classify_success, classify_response = self.run_test(
            "E2E - Classification",
            "POST",
            "classify",
            200,
            files=files
        )
        
        if not classify_success:
            return False
        
        # Step 2: Get advisory using classification result
        advisory_data = {
            "crop_name": "Tomato",
            "disease_label": classify_response['label'],
            "confidence": classify_response['confidence'],
            "image_base64": base64.b64encode(test_image).decode('utf-8')
        }
        
        advisory_success, advisory_response = self.run_test(
            "E2E - Advisory",
            "POST",
            "advisory",
            200,
            data=advisory_data
        )
        
        if advisory_success:
            print(f"✅ End-to-end flow completed successfully")
            print(f"   Disease: {classify_response['label']}")
            print(f"   Confidence: {classify_response['confidence']:.2f}")
            print(f"   Severity: {advisory_response['severity']}")
        
        return classify_success and advisory_success

def main():
    print("🌱 CropSense AI Backend API Testing")
    print("=" * 50)
    
    tester = CropSenseAPITester()
    
    # Run all tests
    tests = [
        ("API Root", tester.test_root_endpoint),
        ("Status Endpoints", tester.test_status_endpoints),
        ("Disease Classification", tester.test_classify_endpoint),
        ("Treatment Advisory", tester.test_advisory_endpoint),
        ("Multi-language Advisory", tester.test_advisory_multilanguage),
        ("History CRUD Operations", tester.test_history_endpoints),
        ("End-to-End Flow", tester.test_end_to_end_flow)
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            test_func()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            tester.tests_run += 1
    
    # Print final results
    print(f"\n{'='*50}")
    print(f"📊 Final Results:")
    print(f"   Tests Run: {tester.tests_run}")
    print(f"   Tests Passed: {tester.tests_passed}")
    print(f"   Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print(f"🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())