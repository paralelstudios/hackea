//
//  OrganizationDetailsViewController.swift
//  Causa
//
//  Created by Pixnabi on 4/2/17.
//  Copyright © 2017 Pixnabilab. All rights reserved.
//

import UIKit
import MessageUI

class OrganizationDetailsViewController: UIViewController, MFMailComposeViewControllerDelegate {
    
    @IBOutlet weak var orgNameLabel: UILabel!
    @IBOutlet weak var missionLabel: UILabel!
    @IBOutlet weak var servicesLabel: UILabel!
    @IBOutlet weak var locationLabel: UILabel!
    @IBOutlet weak var favImgView: UIImageView!
    @IBOutlet weak var contactLabel: UILabel!
    
    var organization: [String:Any]!
    
    var isFav = false
    let noFav = UIImage(named: "favs.png")!
    let fav = UIImage(named: "patrick.png")!

    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
        //["mission": , "name": CODERI, "email": , "registered": 0, "timestamp": 2017-04-01T15:36:26, "location": , "desires": donaciones monetarias, donaciones de recursos, "id": ca7567e1-b464-481f-a5ca-4acc50440b01, "services": Servicios educativos, "phone": , "fb": , "fiveoone": 0, "candidates": ]
        if let org = self.organization {
            if let name = org["name"] as? String {
                self.orgNameLabel.text = name
            }
            if let mission = org["mission"] as? String {
                self.missionLabel.text = mission
            }
            if let services = org["services"] as? String {
                self.servicesLabel.text = services
            }
            if let services = org["location"] as? String {
                self.locationLabel.text = services
            }
            if let email = org["email"] as? String {
                self.contactLabel.text = email
            }
            if let phone = org["phone"] as? String {
                self.contactLabel.text = "\(self.contactLabel.text!)\n\(phone)"
            }
        }
    }
    
    @IBAction func callOrganization(_ sender: UIButton) {
        if let phone = organization["phone"] as? String {
            var cleanStr = phone.replacingOccurrences(of: "(", with: "")
            cleanStr = phone.replacingOccurrences(of: ")", with: "")
            cleanStr = phone.replacingOccurrences(of: "-", with: "")
            cleanStr = phone.replacingOccurrences(of: " ", with: "")
            if let url = URL(string: "tel://\(cleanStr)") {
                UIApplication.shared.openURL(url)
            }
        }
    }
    
    @IBAction func addFavorite(_ sender: UIButton) {
        if isFav {
            self.favImgView.image = noFav
        } else {
            self.favImgView.image = fav
        }
        isFav = !isFav
    }
    
    @IBAction func emailOrganization(_ sender: UIButton) {
        if let email = organization["email"] as? String {
            let composeVC = MFMailComposeViewController()
            composeVC.mailComposeDelegate = self
            // Configure the fields of the interface.
            composeVC.setToRecipients(["\(email)"])
            // Present the view controller modally.
            self.present(composeVC, animated: true, completion: nil)
        }
    }
    
    func mailComposeController(_ controller: MFMailComposeViewController, didFinishWith result: MFMailComposeResult, error: Error?) {
        controller.dismiss(animated: true, completion: nil)
    }
}
