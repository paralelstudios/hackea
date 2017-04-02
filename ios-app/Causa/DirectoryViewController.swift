//
//  DirectoryViewController.swift
//  Causa
//
//  Created by Pixnabi on 4/1/17.
//  Copyright © 2017 Pixnabilab. All rights reserved.
//

import UIKit
import MBProgressHUD

class DirectoryViewController: UIViewController {
    
    @IBOutlet weak var tableView: UITableView!
    @IBOutlet weak var searchBar: UISearchBar!
    
    var orgs = NSArray()
    var filtered = NSArray()
    var index = 0
    
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        let indicator = MBProgressHUD.showAdded(to: self.view, animated: true)
        indicator.bezelView.color = UIColor(rgb: 0x4A999A)
        Cause.getOrganizations(name: nil) { (success, response, error) in
            indicator.hide(animated: true)
            if let err = error {
                print("Error getting orgs: \(err)")
            }
            if let data = response {
                if let orgs = data["orgs"] as? NSArray {
                    self.orgs = orgs
                    self.filtered = orgs
                    self.tableView.reloadData()
                }
            } else {
                print("Directory error: \(error)")
            }
        }
    }
    
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        if segue.identifier == "viewOrganization" {
            let orgView = segue.destination as! OrganizationDetailsViewController
            if let org = self.orgs[self.index] as? String {
                if let dict = self.convertToDictionary(text: org) {
                    orgView.organization = dict
                }
            }
        }
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        self.navigationItem.title = "Directorio"
        // Do any additional setup after loading the view.
        self.tabBarController?.tabBar.unselectedItemTintColor = UIColor.white
        self.tableView.estimatedRowHeight = 80
        self.tableView.rowHeight = UITableViewAutomaticDimension
    }
    
}

extension DirectoryViewController: UITableViewDelegate, UITableViewDataSource, UISearchBarDelegate {
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return self.filtered.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "Cell", for: indexPath) as! DirectoryCell
        if let data = self.filtered[indexPath.row] as? String{
            //            print("Cell data: \(data)")
            cell.loadCell(data: data)
        }
        return cell
    }
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        self.index = indexPath.row
        self.performSegue(withIdentifier: "viewOrganization", sender: self)
    }
    
    func searchBarCancelButtonClicked(_ searchBar: UISearchBar) {
        searchBar.resignFirstResponder()
        searchBar.showsCancelButton = false
    }
    
    func searchBarTextDidEndEditing(_ searchBar: UISearchBar) {
        searchBar.showsCancelButton = false
    }
    
    func searchBarTextDidBeginEditing(_ searchBar: UISearchBar) {
        searchBar.showsCancelButton = true
    }
    
    
    func searchBarSearchButtonClicked(_ searchBar: UISearchBar) {
        searchBar.resignFirstResponder()
        searchBar.showsCancelButton = false
    }
    
    func searchBar(_ searchBar: UISearchBar, textDidChange searchText: String) {
        
        //        print("search: \(searchText)")
        filtered = self.orgs.filter({ (org) -> Bool in
            if let org = org as? String {
                if let dict = self.convertToDictionary(text: org) {
                    if let tmp: NSString = dict["name"] as? NSString {
                        let range = tmp.range(of: searchText, options: NSString.CompareOptions.regularExpression)
                        return range.location != NSNotFound
                    }
                }
            }
            return false
        }) as NSArray
        if self.filtered.count == 0 {
            filtered = self.orgs.filter({ (org) -> Bool in
                if let org = org as? String {
                    if let dict = self.convertToDictionary(text: org) {
                        if let tmp: NSString = dict["services"] as? NSString {
                            let range = tmp.range(of: searchText, options: NSString.CompareOptions.regularExpression)
                            return range.location != NSNotFound
                        }
                    }
                }
                return false
            }) as NSArray
        }
        if self.filtered.count == 0 {
            filtered = self.orgs.filter({ (org) -> Bool in
                if let org = org as? String {
                    if let dict = self.convertToDictionary(text: org) {
                        if let tmp: NSString = dict["mission"] as? NSString {
                            let range = tmp.range(of: searchText, options: NSString.CompareOptions.regularExpression)
                            return range.location != NSNotFound
                        }
                    }
                }
                return false
            }) as NSArray        }
        if searchText.isEmpty || searchText == "" {
            self.filtered = self.orgs
        }
        self.tableView.reloadData()
    }
    
    func convertToDictionary(text: String) -> [String: Any]? {
        if let data = text.data(using: .utf8) {
            do {
                return try JSONSerialization.jsonObject(with: data, options: []) as? [String: Any]
            } catch {
                print(error.localizedDescription)
            }
        }
        return nil
    }
}


class DirectoryCell: UITableViewCell {
    
    @IBOutlet weak var nameLabel: UILabel!
    @IBOutlet weak var missionLabel: UILabel!
    @IBOutlet weak var categoryLabel: UILabel!
    
    func loadCell(data: String) {
        //        self.nameLabel.text = nil
        //        self.missionLabel.text = nil
        //        self.categoryLabel.text = nil
        if let dict = convertToDictionary(text: data) {
            print("dict: \(dict)")
            //["mission": , "name": CODERI, "email": , "registered": 0, "timestamp": 2017-04-01T15:36:26, "location": , "desires": donaciones monetarias, donaciones de recursos, "id": ca7567e1-b464-481f-a5ca-4acc50440b01, "services": Servicios educativos, "phone": , "fb": , "fiveoone": 0, "candidates": ]
            if let name = dict["name"] as? String {
                self.nameLabel.text = name
            }
            if let mission = dict["mission"] as? String {
                self.missionLabel.text = mission
            }
            if let services = dict["services"]as? String {
                self.categoryLabel.text = services
            }
        }
        self.selectionStyle = .none
        
    }
    func convertToDictionary(text: String) -> [String: Any]? {
        if let data = text.data(using: .utf8) {
            do {
                return try JSONSerialization.jsonObject(with: data, options: []) as? [String: Any]
            } catch {
                print(error.localizedDescription)
            }
        }
        return nil
    }
}
