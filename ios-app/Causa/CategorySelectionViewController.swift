//
//  CategorySelectionViewController.swift
//  Causa
//
//  Created by Pixnabi on 4/1/17.
//  Copyright © 2017 Pixnabilab. All rights reserved.
//

import UIKit

class CategorySelectionViewController: UIViewController {
    
    @IBOutlet weak var tableView: UITableView!
    
    var registrationView: RegisterOrganizationViewController!
    
    var selected = [Bool]()
    var selectedCategories = [String]()
    
    var doneSelecting: UIBarButtonItem!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        self.doneSelecting = UIBarButtonItem(title: "Seleccionar", style: .plain, target: self, action: #selector(self.doneSelectingCategories))
        self.navigationItem.leftBarButtonItem = self.doneSelecting
        // Do any additional setup after loading the view.
        for _ in organizationCategories.enumerated() {
            self.selected.append(false)
        }
    }
    
    func doneSelectingCategories() {
        if let vc = self.registrationView {
            vc.categoryLabel.text = ""
            if self.selectedCategories.count == 0 {
                vc.categoryLabel.text = "Categorías:"
            }
            for selected in self.selectedCategories {
                vc.categoryLabel.text = "\(vc.categoryLabel.text!)\n\(selected)"
            }
        }
        self.navigationController?.popViewController(animated: true)
    }
    
    
}

extension CategorySelectionViewController: UITableViewDelegate, UITableViewDataSource {
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return organizationCategories.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "Cell", for: indexPath)
        cell.textLabel?.textAlignment = .center
        cell.textLabel?.textColor = UIColor(rgb: 0x4A999A)
        let category = organizationCategories[indexPath.row]
        cell.textLabel?.text = category
        cell.accessoryType = .none
        if self.selected[indexPath.row] {
            cell.accessoryType = .checkmark
        }
        return cell
    }
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        let check = self.selected[indexPath.row]
        self.selected[indexPath.row] = !check
        if let cell = tableView.cellForRow(at: indexPath) {
            if check {
                cell.accessoryType = .none
                let category = organizationCategories[indexPath.row]
                if let index = self.selectedCategories.index(of: category) {
                    self.selectedCategories.remove(at: index)
                }
            } else {
                cell.accessoryType = .checkmark
                let category = organizationCategories[indexPath.row]
                self.selectedCategories.append(category)
            }
            print("Selected: \(selectedCategories)")
        }
    }
}
