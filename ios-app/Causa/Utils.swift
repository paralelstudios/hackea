//
//  Utils.swift
//  Vendy
//
//  Created by Pablo A. Rivera on 10/2/15.
//  Copyright © 2015 Pablo A. Rivera. All rights reserved.
//

class Utils: NSObject {
    
    // MARK: Show Simple Alert Message
    class func showSimpleAlertWithTitle(_ title: String!, message: String, viewController: UIViewController) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        let action = UIAlertAction(title: "OK", style: .cancel, handler: nil)
        alert.addAction(action)
        viewController.present(alert, animated: true, completion: nil)
    }
    
    // MARK: ImagePicker Utils
    class func showImagepicker(_ viewController: UIViewController, imagePicker: UIImagePickerController, title: String?, message: String?) {
        let alert = UIAlertController(title: title != nil ? title : "", message: message != nil ? message : "Chose from Library or New Picture", preferredStyle:   UIAlertControllerStyle.alert)
        
        let select = UIAlertAction(title: "Galería", style: UIAlertActionStyle.default) { (library) -> Void in
            imagePicker.sourceType = UIImagePickerControllerSourceType.photoLibrary
            viewController.present(imagePicker, animated: true, completion: nil)
        }
        if UIImagePickerController.isSourceTypeAvailable(UIImagePickerControllerSourceType.camera){
            let newPic = UIAlertAction(title: "Nueva Foto", style: UIAlertActionStyle.default) { (library) -> Void in
                imagePicker.sourceType = UIImagePickerControllerSourceType.camera
                imagePicker.cameraDevice = .rear
                viewController.present(imagePicker, animated: true, completion: nil)
                
            }
            alert.addAction(newPic)
        }
        
        let cancel = UIAlertAction(title: "Cancelar", style: UIAlertActionStyle.cancel, handler: nil)
        alert.addAction(select)
        alert.addAction(cancel)
        viewController.present(alert, animated: true, completion: nil)
    }
}
