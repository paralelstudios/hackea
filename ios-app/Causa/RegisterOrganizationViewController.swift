//
//  RegisterOrganizationViewController.swift
//  Causa
//
//  Created by Pixnabi on 4/1/17.
//  Copyright © 2017 Pixnabilab. All rights reserved.
//

import UIKit

class RegisterOrganizationViewController: UIViewController {
    
    @IBOutlet weak var nameField: UITextField!
//    @IBOutlet weak var imageView: UIImageView!
    @IBOutlet weak var missionTextView: UITextView!
    @IBOutlet weak var categoryLabel: UILabel!

    let toolBar = UIToolbar()
    
    
    override func viewDidLoad() {
        super.viewDidLoad()
        toolBar.barStyle = UIBarStyle.default
        toolBar.isTranslucent = true
        toolBar.sizeToFit()
        let doneButton = UIBarButtonItem(title: "Cerrar", style: UIBarButtonItemStyle.plain, target: self, action: #selector(self.resignResponder))
        doneButton.tintColor = UIColor(rgb: 0x4A999A)
        toolBar.setItems([doneButton], animated: false)
        toolBar.isUserInteractionEnabled = true
        // Do any additional setup after loading the view.
        self.title = "Registrar Organización"
//        self.imageView.clipsToBounds = true
//        self.imageView.layer.cornerRadius = 5
//        self.imageView.layer.borderWidth = 1
//        self.imageView.layer.borderColor = UIColor(rgb: 0x79C2C8).cgColor
        
        self.missionTextView.inputAccessoryView = self.toolBar
        self.missionTextView.layer.cornerRadius = 5
        self.missionTextView.layer.borderWidth = 1
        self.missionTextView.layer.borderColor = UIColor(rgb: 0x79C2C8).cgColor
    }
    
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        if segue.identifier == "selectCategory" {
            let categoryView = segue.destination as! CategorySelectionViewController
            categoryView.registrationView = self
        }
    }
    
    func resignResponder() {
        self.missionTextView.resignFirstResponder()
    }
    
    @IBAction func addLogoImage(_ sender: UIButton) {
        let imagePicker = UIImagePickerController()
        imagePicker.delegate = self
        Utils.showImagepicker(self, imagePicker: imagePicker, title: "Logo Icono", message: "Escoger opción")
    }
    
    @IBAction func selectCategory(_ sender: UIButton) {
        self.performSegue(withIdentifier: "selectCategory", sender: self)
    }
    
    @IBAction func registerOrganization(_ sender: UIButton) {
        if let name = self.nameField.text {
            if name.isEmpty {
                return
            }
            if let userId = UserDefaults.standard.string(forKey: "userId") {
                print("user id: \(userId)")
                Cause.registerOrganization(name: name, userId: userId, completionHandler: { (success, response, error) in
                    if success {
                        if let data = response {
                            print("Org registration data: \(data)")
                            if let orgSuccess = data["success"] as? Bool{
                                if orgSuccess{
                                    Utils.showSimpleAlertWithTitle("¡Gracias!", message: "Su organización fue registrada.", viewController: self)
                                }
                            }
                        }
                    }
                })
            }
        }
    }
}

// Image picker delegate

extension RegisterOrganizationViewController: UIImagePickerControllerDelegate, UINavigationControllerDelegate {
    func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [String : Any]) {
        if let chosenImage = info[UIImagePickerControllerOriginalImage] as? UIImage {
//            self.imageView.image = chosenImage
        }
        picker.dismiss(animated: true, completion: nil)
    }
}
