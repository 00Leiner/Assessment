<?php

namespace App\Http\Controllers;

use App\Models\Contact;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;
use Illuminate\Database\Eloquent\ModelNotFoundException;

class ContactController extends Controller
{
    // upload to 'storage/app/contacts/' 
    public function upload(Request $request)
    {
        try {
            // Validate the uploaded file
            $validator = Validator::make($request->all(), [
                'file' => 'required|mimes:json|max:2048', // JSON file, max size 2MB
            ]);

            // Error handling
            if ($validator->fails()) {
                return $this->errorResponse($validator->errors()->first(), 400);
            }

            // Define the path
            $storagePath = storage_path('app/contacts');

            // Create the directory 
            if (!file_exists($storagePath)) {
                mkdir($storagePath, 0755, true); 
            }
            
            // Store the file in 'storage/app/contacts/' 
            $path = $request->file('file')->store('contacts');

            return $this->successResponse(['path' => $path], 'File uploaded successfully');

        } catch (\Exception $e) {
            return $this->errorResponse('File upload failed: ' . $e->getMessage(), 500);
        }
    }

    // get all
    public function contacts(Request $request)
    {
        try {
            $query = Contact::query();

            // Search by name or email
            if ($request->has('search')) {
                $search = $request->input('search');
                $query->where(function ($q) use ($search) {
                    $q->where('name', 'like', "%{$search}%")
                      ->orWhere('email', 'like', "%{$search}%");
                });
            }

            // Pagination
            $contacts = $query->paginate(10); 

            return $this->successResponse($contacts);
            
        } catch (\Exception $e) {
            return $this->errorResponse('Failed to retrieve contacts: ' . $e->getMessage(), 500);
        }
    }
    
    // get a single contact by ID
    public function retrieve($id)
    {
        try {
            $contact = Contact::findOrFail($id);
            return $this->successResponse($contact);
        } catch (ModelNotFoundException $e) {
            return $this->errorResponse('Contact not found', 404);
        } catch (\Exception $e) {
            return $this->errorResponse('Failed to retrieve contact: ' . $e->getMessage(), 500);
        }
    }

    // add 
    public function add(Request $request)
    {
        try {
            $request->validate(Contact::$rules); // Use validation rules from the model

            $contact = Contact::create($request->all());
            return $this->successResponse($contact, 'Contact created successfully', 201);
        } catch (\Exception $e) {
            return $this->errorResponse('Failed to create contact: ' . $e->getMessage(), 500);
        }
    }

    // update a contact by ID
    public function update(Request $request, $id)
    {
        try {
            $contact = Contact::findOrFail($id);
            
            $request->validate(array_merge(Contact::$rules, [
                'email' => 'sometimes|required|email|max:255|unique:contacts,email,' . $id,
            ]));

            $contact->update($request->all());
            return $this->successResponse($contact);
        } catch (ModelNotFoundException $e) {
            return $this->errorResponse('Contact not found', 404);
        } catch (\Exception $e) {
            return $this->errorResponse('Failed to update contact: ' . $e->getMessage(), 500);
        }
    }

    // delete a contact by ID
    public function delete($id)
    {
        try {
            $contact = Contact::findOrFail($id);
            $contact->delete();
            return $this->successResponse([], 'Contact deleted successfully');
        } catch (ModelNotFoundException $e) {
            return $this->errorResponse('Contact not found', 404);
        } catch (\Exception $e) {
            return $this->errorResponse('Failed to delete contact: ' . $e->getMessage(), 500);
        }
    }
}
